from __future__ import annotations

from typing import Dict

from tasks.common import clamp01, require_valid_final_state


def grade_hard(state: Dict[str, float]) -> float:
    require_valid_final_state(state)

    users = float(state["users"])
    team_size = max(float(state["team_size"]), 1.0)
    money = float(state["money"])

    efficiency_score = clamp01((users / team_size) / 250.0)
    cash_discipline_score = clamp01((money - 400.0) / 5200.0)
    satisfaction_score = clamp01(float(state["customer_satisfaction"]))
    execution_score = min(efficiency_score, satisfaction_score)

    base = (
        (0.40 * efficiency_score)
        + (0.25 * cash_discipline_score)
        + (0.20 * satisfaction_score)
        + (0.15 * execution_score)
    )

    score = clamp01((0.55 * base) - 0.05)
    return round(score, 6)
