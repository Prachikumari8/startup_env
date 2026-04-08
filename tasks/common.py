from __future__ import annotations

from typing import Dict


ALLOWED_TERMINAL_STATUS = {"running", "bankrupt", "horizon_reached"}


def clamp01(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def require_valid_final_state(state: Dict[str, float]) -> None:
    required = {
        "money",
        "users",
        "team_size",
        "product_quality",
        "customer_satisfaction",
        "status",
    }
    missing = required.difference(state.keys())
    if missing:
        raise ValueError(f"State is missing required keys: {sorted(missing)}")

    money = float(state["money"])
    users = float(state["users"])
    team_size = float(state["team_size"])
    product_quality = float(state["product_quality"])
    satisfaction = float(state["customer_satisfaction"])
    status = str(state["status"])

    if users < 0:
        raise ValueError("Invalid state: users cannot be negative.")
    if team_size < 1:
        raise ValueError("Invalid state: team_size must be at least 1.")
    if product_quality < 0:
        raise ValueError("Invalid state: product_quality cannot be negative.")
    if not 0.0 <= satisfaction <= 1.0:
        raise ValueError("Invalid state: customer_satisfaction must be within [0, 1].")
    if status not in ALLOWED_TERMINAL_STATUS:
        raise ValueError(f"Invalid state: unknown status '{status}'.")

    if status != "bankrupt" and money < 0:
        raise ValueError("Invalid state: non-bankrupt episodes cannot have negative money.")