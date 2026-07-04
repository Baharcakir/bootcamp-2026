"""Konu bazlı ustalık kestirimi — Çarpan'ın veri bilimi çekirdeği.

Yaklaşım: Beta-Binomial modeli.
- Her konuda doğru sayısını Binomial, başarı olasılığını Beta önseliyle modelleriz.
- Az soruyla yanıltıcı kesinlik vermemek için nokta tahminin yanında %90 güven aralığı üretiriz.
- Eski denemelerin etkisini üstel unutma ile azaltırız (yarı ömür: 30 gün) — iki ay önceki
  başarısızlık, dünkü başarıyı gölgelemez.
- Boş bırakılan soru "henüz bilinmiyor" sayılır (başarısızlık tarafına yazılır).
- 5 şıklı testte şans başarısını (p=0.2) düzelterek "gerçek bilgi" kestirimi ekleriz.

Çalışma önceliği: konunun sınavdaki soru ağırlığı × (1 − kötümser ustalık). Böylece hem zayıf
hem de henüz belirsiz konular öne çıkar; sınavda çok soru getiren konular önceliklenir.

TODO(A4 — Sprint 2): parametreleri (yarı ömür, önsel) sentetik veriyle kalibre et, raporla.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from scipy.stats import beta as beta_dist

HALF_LIFE_DAYS = 30.0
PRIOR_ALPHA = 1.0
PRIOR_BETA = 1.0
GUESS_RATE = 0.20
CI_LEVEL = 0.90


@dataclass(frozen=True)
class TopicObservation:
    """Tek denemedeki tek konunun sonucu."""

    subject: str
    topic: str
    exam_date: date
    correct: int
    wrong: int
    blank: int


@dataclass(frozen=True)
class TopicMastery:
    subject: str
    topic: str
    effective_attempts: float  # unutma ağırlıklı etkin soru sayısı
    mastery: float  # posterior ortalama
    ci_low: float  # %90 aralığın alt ucu (kötümser kestirim)
    ci_high: float
    knowledge: float  # şans düzeltmeli "gerçek bilgi" kestirimi


def _recency_weight(exam_date: date, today: date) -> float:
    age_days = max((today - exam_date).days, 0)
    return 0.5 ** (age_days / HALF_LIFE_DAYS)


def estimate_mastery(
    observations: list[TopicObservation], today: date | None = None
) -> list[TopicMastery]:
    today = today or date.today()
    # (ders, konu) -> [etkin başarı, etkin başarısızlık]
    acc: dict[tuple[str, str], list[float]] = {}
    for obs in observations:
        w = _recency_weight(obs.exam_date, today)
        cur = acc.setdefault((obs.subject, obs.topic), [0.0, 0.0])
        cur[0] += w * obs.correct
        cur[1] += w * (obs.wrong + obs.blank)

    tail = (1 - CI_LEVEL) / 2
    results = []
    for (subject, topic), (success, failure) in sorted(acc.items()):
        a = PRIOR_ALPHA + success
        b = PRIOR_BETA + failure
        mean = a / (a + b)
        ci_low = float(beta_dist.ppf(tail, a, b))
        ci_high = float(beta_dist.ppf(1 - tail, a, b))
        knowledge = max(0.0, (mean - GUESS_RATE) / (1 - GUESS_RATE))
        results.append(
            TopicMastery(subject, topic, success + failure, mean, ci_low, ci_high, knowledge)
        )
    return results


def study_priorities(
    masteries: list[TopicMastery],
    topic_weights: dict[tuple[str, str], float] | None = None,
    top: int | None = None,
) -> list[tuple[TopicMastery, float]]:
    """Konuları çalışma önceliğine göre sıralar.

    Öncelik = sınav ağırlığı × (1 − ci_low). ci_low kötümser ustalık olduğundan, kesin zayıf
    konular kadar "belirsiz" konular da (az veri) yüksek öncelik alır: önce teşhis, sonra tedavi.
    """
    weights = topic_weights or {}
    scored = [
        (m, weights.get((m.subject, m.topic), 1.0) * (1.0 - m.ci_low)) for m in masteries
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top] if top else scored
