from __future__ import annotations

from typing import Dict, Tuple


def validate_terminal(day: int, max_days: int, money: float) -> Tuple[bool, str]:
    if money <= 0:
        return True, "bankrupt"
    if day >= max_days:
        return True, "horizon_reached"
    return False, "running"


def validate_action(action: str) -> None:
    allowed = {"hire", "market", "build", "support", "idle"}
    if action not in allowed:
        raise ValueError(f"Invalid action: {action}. Allowed: {sorted(allowed)}")


def state_snapshot(values: Dict[str, float]) -> Dict[str, float]:
    return dict(values)
