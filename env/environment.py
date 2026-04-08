from __future__ import annotations

from random import Random
from typing import Dict, List, Optional, Tuple

from env.dynamics import apply_action
from env.utils import clamp, rolling_idle_penalty
from env.validation import state_snapshot, validate_action, validate_terminal
from models import Action, Observation, Reward


class StartupOperationsEnv:
    """OpenEnv-compatible startup operations environment."""

    def __init__(self, max_days: int = 30, seed: int = 42):
        self.max_days = max_days
        self.seed = seed
        self._rng = Random(seed)
        self._actions_history: List[str] = []
        self._status = "not_started"
        self.reset(seed=seed)

    def reset(self, seed: Optional[int] = None) -> Observation:
        if seed is not None:
            self.seed = seed
        self._rng = Random(self.seed)
        self.day = 0
        self.money = 1600.0
        self.users = 120
        self.team_size = 3
        self.product_quality = 1.0
        self.customer_satisfaction = 0.62
        self.market_demand = 1.0
        self.burn_rate = 0.0
        self.last_action = "reset"
        self._status = "running"
        self._actions_history = []
        return self._get_observation()

    def state(self) -> Dict[str, float]:
        return state_snapshot(
            {
                "day": self.day,
                "money": round(self.money, 3),
                "users": self.users,
                "team_size": self.team_size,
                "product_quality": round(self.product_quality, 3),
                "customer_satisfaction": round(self.customer_satisfaction, 3),
                "market_demand": round(self.market_demand, 3),
                "burn_rate": round(self.burn_rate, 3),
                "last_action": self.last_action,
                "status": self._status,
            }
        )

    def _get_observation(self) -> Observation:
        return Observation(
            day=self.day,
            money=round(self.money, 3),
            users=self.users,
            team_size=self.team_size,
            product_quality=round(self.product_quality, 3),
            customer_satisfaction=round(self.customer_satisfaction, 3),
            market_demand=round(self.market_demand, 3),
            burn_rate=round(self.burn_rate, 3),
            last_action=self.last_action,
        )

    def _reward(self, transition: Dict[str, float], action: str) -> float:
        growth_signal = clamp(transition["gross_new_users"] / 100.0, 0.0, 1.0)
        quality_signal = clamp((self.product_quality - 0.8) / 1.4, 0.0, 1.0)
        finance_signal = clamp(self.money / 3000.0, 0.0, 1.0)
        satisfaction_signal = clamp(self.customer_satisfaction, 0.0, 1.0)

        penalty = 0.0
        if self.money < 250:
            penalty -= 0.25
        penalty += rolling_idle_penalty(self._actions_history, threshold=3)
        if action == "hire" and self.money < 500:
            penalty -= 0.1

        shaped = (
            (0.32 * growth_signal)
            + (0.26 * quality_signal)
            + (0.26 * finance_signal)
            + (0.16 * satisfaction_signal)
            + penalty
        )
        return clamp(shaped, 0.0, 1.0)

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, float]]:
        if self._status != "running":
            raise RuntimeError("Episode has ended. Call reset() to start a new one.")

        validate_action(action.action_type)
        self.day += 1
        self.last_action = action.action_type
        self._actions_history.append(action.action_type)

        transition = apply_action(self.state(), action.action_type, self._rng)

        self.money = transition["money"]
        self.users = int(transition["users"])
        self.team_size = int(transition["team_size"])
        self.product_quality = transition["product_quality"]
        self.customer_satisfaction = transition["customer_satisfaction"]
        self.market_demand = transition["market_demand"]
        self.burn_rate = transition["burn_rate"]

        done, terminal_reason = validate_terminal(self.day, self.max_days, self.money)
        if done:
            self._status = terminal_reason

        reward_value = self._reward(transition, action.action_type)
        reward = Reward(value=reward_value)
        info: Dict[str, float] = {
            "terminal_reason": terminal_reason,
            "revenue": round(transition["revenue"], 3),
            "expense": round(transition["expense"], 3),
            "gross_new_users": int(transition["gross_new_users"]),
            "churned_users": int(transition["churned_users"]),
        }

        return self._get_observation(), reward, done, info
