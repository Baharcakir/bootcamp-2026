from datetime import date, timedelta

from app.services.mastery import TopicObservation, estimate_mastery, study_priorities

TODAY = date(2026, 7, 2)


def obs(topic="Problemler", days_ago=0, correct=0, wrong=0, blank=0, subject="Matematik"):
    return TopicObservation(
        subject, topic, TODAY - timedelta(days=days_ago), correct, wrong, blank
    )


def mastery_of(observations, topic):
    results = estimate_mastery(observations, today=TODAY)
    return next(m for m in results if m.topic == topic)


def test_iyi_performans_yuksek_ustalik():
    m = mastery_of([obs(correct=9, wrong=1)], "Problemler")
    assert m.mastery > 0.7


def test_kotu_performans_dusuk_ustalik():
    m = mastery_of([obs(correct=1, wrong=9)], "Problemler")
    assert m.mastery < 0.3


def test_bos_sorular_bilinmiyor_sayilir():
    m = mastery_of([obs(correct=2, blank=8)], "Problemler")
    assert m.mastery < 0.5


def test_veri_arttikca_guven_araligi_daralir():
    az_veri = mastery_of([obs(correct=3, wrong=1)], "Problemler")
    cok_veri = mastery_of([obs(correct=30, wrong=10)], "Problemler")
    assert (cok_veri.ci_high - cok_veri.ci_low) < (az_veri.ci_high - az_veri.ci_low)


def test_eski_kotu_veri_yeni_iyi_veriyi_golgelemez():
    gecmis_kotu = obs(days_ago=90, correct=1, wrong=9)
    yeni_iyi = obs(days_ago=1, correct=9, wrong=1)
    m = mastery_of([gecmis_kotu, yeni_iyi], "Problemler")
    assert m.mastery > 0.6


def test_sans_duzeltmesi():
    # %20 doğru ≈ tamamen şansla açıklanabilir → gerçek bilgi ~0
    m = mastery_of([obs(correct=8, wrong=32)], "Problemler")
    assert m.knowledge < 0.05


def test_oncelik_agirlik_ve_zayifliga_gore_siralar():
    observations = [
        obs(topic="Problemler", correct=2, wrong=8),  # zayıf + yüksek ağırlık
        obs(topic="Kümeler", correct=9, wrong=1),  # güçlü
    ]
    weights = {("Matematik", "Problemler"): 3.0, ("Matematik", "Kümeler"): 1.0}
    ranked = study_priorities(estimate_mastery(observations, today=TODAY), weights)
    assert ranked[0][0].topic == "Problemler"
    assert ranked[0][1] > ranked[1][1]
