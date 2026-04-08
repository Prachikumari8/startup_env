from __future__ import annotations

from typing import Dict


def heuristic_action(state: Dict[str, float]) -> str:
    if state["money"] < 220:
        return "idle"
    if state["customer_satisfaction"] < 0.5:
        return "support"
    if state["product_quality"] < 1.3:
        return "build"
    if state["users"] < 450 and state["money"] > 320:
        return "market"
    if state["team_size"] < 6 and state["money"] > 700:
        return "hire"
    return "market"
