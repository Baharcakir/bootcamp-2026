"""Net gidişatı — v0: doğrusal eğilim taban çizgisi.

TODO(A5 — Sprint 3): sentetik kohortla (A3 üreteci) eğitilmiş GradientBoosting regresyonuna
yükselt; girdiler: son N denemenin konu ustalıkları + ders netleri. Bu taban çizgisiyle
karşılaştırmalı değerlendirme raporu repoya eklenecek.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np


@dataclass(frozen=True)
class ExamNet:
    taken_on: date
    name: str
    net: float


@dataclass(frozen=True)
class TrendResult:
    history: list[ExamNet]
    slope_per_week: float  # haftalık net değişimi
    predicted_next: float | None  # ~1 hafta sonrası için kestirim


def compute_net(correct: int, wrong: int) -> float:
    """YKS kuralı: 4 yanlış 1 doğruyu götürür."""
    return correct - wrong / 4.0


def net_trend(history: list[ExamNet]) -> TrendResult:
    if not history:
        return TrendResult([], 0.0, None)
    history = sorted(history, key=lambda e: e.taken_on)
    if len(history) == 1:
        return TrendResult(history, 0.0, history[0].net)

    days = np.array([(e.taken_on - history[0].taken_on).days for e in history], dtype=float)
    nets = np.array([e.net for e in history], dtype=float)
    slope, intercept = np.polyfit(days, nets, 1)
    predicted = float(slope * (days[-1] + 7.0) + intercept)
    return TrendResult(history, float(slope * 7.0), predicted)
