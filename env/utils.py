from __future__ import annotations

from typing import Iterable


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def rolling_idle_penalty(last_actions: Iterable[str], threshold: int = 3) -> float:
    trailing = list(last_actions)[-threshold:]
    if len(trailing) < threshold:
        return 0.0
    return -0.08 if all(a == "idle" for a in trailing) else 0.0
