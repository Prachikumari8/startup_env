from __future__ import annotations

from typing import Dict

from tasks.common import clamp01, require_valid_final_state


def grade_easy(state: Dict[str, float]) -> float:
    require_valid_final_state(state)

    # Easy rewards keeping the company healthy with less harsh penalties.
    cash_runway = clamp01(float(state["money"]) / 2600.0)
    quality = clamp01((float(state["product_quality"]) - 0.8) / 1.2)
    satisfaction = clamp01(float(state["customer_satisfaction"]))
    alive_bonus = 1.0 if str(state["status"]) != "bankrupt" else 0.0

    base = (0.35 * cash_runway) + (0.20 * quality) + (0.20 * satisfaction) + (0.25 * alive_bonus)
    score = clamp01((0.40 * base) + 0.60)
    return round(score, 6)
