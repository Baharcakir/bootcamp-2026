"""T6 — Eğitim verisi için doğrulanmış AI soruları üretir (konu başına N adet).

T3'teki üretim+bağımsız çözücü protokolünün toplu hali: üretilen soru, cevabı görmeyen
ikinci bir model çağrısıyla çözdürülür; cevaplar uyuşmazsa soru elenir. Çeşitlilik için
üretici, aynı konuda daha önce ürettiği soruların başlangıçlarını görür ve farklı kurgu
kullanması istenir.

Demir kural (docs/mimari.md "Veri Protokolü"): buradaki AI üretimi sorular YALNIZ eğitim
içindir; 120 soruluk ÖSYM değerlendirme setine asla girmez. Konu saflığı ayrıca
sınıflandırıcı eğitim script'inde metinden yeniden etiketlenerek denetlenir.

Çıktı: data/uretilen_sorular.csv (kendi ürettiğimiz içerik — repoya girebilir)

Çalıştırma (repo kökünden, .env'de GOOGLE_API_KEY ile):
    python backend/scripts/generate_training_questions.py            # tüm konular, 12'şer
    python backend/scripts/generate_training_questions.py 15         # konu başına 15
    python backend/scripts/generate_training_questions.py 12 Kümeler # tek konu

Kaldığı yerden devam eder; kota (429) hatasında bekleyip yeniden dener.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.agents.quiz import GENERATE_PROMPT, SOLVE_PROMPT, _ask, _llm  # noqa: E402
from app.config import settings  # noqa: E402
from app.services.queries import load_topics  # noqa: E402

OUT_CSV = ROOT / "data" / "uretilen_sorular.csv"
FIELDS = ["konu", "soru", "secenekler", "dogru", "cozum"]
SLEEP_SECONDS = 4
QUOTA_WAIT_SECONDS = 60
MAX_QUOTA_RETRIES = 5

DIVERSITY_NOTE = """

Bu konuda daha önce üretilen soruların başlangıçları şunlar; bunlardan BELİRGİN biçimde
farklı bir kurgu ve farklı sayılar kullan:
{onceki}"""


def math_topics() -> list[str]:
    data = load_topics()
    return next(s["topics"] for s in data["subjects"] if s["name"] == "Matematik")


def load_existing() -> dict[str, list[str]]:
    """Konu -> mevcut soru metinleri (devam edebilme ve çeşitlilik için)."""
    if not OUT_CSV.exists():
        return {}
    by_topic: dict[str, list[str]] = {}
    for r in csv.DictReader(OUT_CSV.open(encoding="utf-8")):
        by_topic.setdefault(r["konu"], []).append(r["soru"])
    return by_topic


def ask_with_quota_retry(llm, prompt: str) -> dict:
    """429/kota hatasında bekleyip yeniden dener; başka hatayı yukarı fırlatır."""
    for attempt in range(MAX_QUOTA_RETRIES):
        try:
            return _ask(llm, prompt)
        except Exception as exc:  # noqa: BLE001 — kota tespiti için mesaja bakıyoruz
            text = str(exc).lower()
            if any(k in text for k in ("429", "quota", "rate", "exhausted", "resource")):
                print(f"    kota/limit ({attempt + 1}/{MAX_QUOTA_RETRIES}) — "
                      f"{QUOTA_WAIT_SECONDS}s bekleniyor", flush=True)
                time.sleep(QUOTA_WAIT_SECONDS)
                continue
            raise
    raise SystemExit(
        "Kota art arda 5 kez doldu — büyük ihtimalle günlük limit. "
        "Script kaldığı yerden devam eder; daha sonra tekrar çalıştır."
    )


def generate_one(topic: str, previous: list[str]) -> dict | None:
    """Tek doğrulanmış soru üretir; doğrulanamazsa None."""
    prompt = GENERATE_PROMPT.format(topic=topic)
    if previous:
        stems = "\n".join(f"- {s[:70]}..." for s in previous[-6:])
        prompt += DIVERSITY_NOTE.format(onceki=stems)

    uretim = ask_with_quota_retry(_llm(temperature=0.9), prompt)
    secenekler = uretim.get("secenekler") or {}
    dogru = str(uretim.get("dogru", "")).strip().upper()
    soru = " ".join(str(uretim.get("soru", "")).split())
    if not soru or dogru not in secenekler or len(secenekler) != 5:
        return None

    # Yinelenen kurguları ele (ilk 60 karakter aynıysa aynı soru say)
    if any(soru[:60] == p[:60] for p in previous):
        return None

    time.sleep(SLEEP_SECONDS)
    sec_metni = "\n".join(f"{h}) {m}" for h, m in sorted(secenekler.items()))
    cozucu = ask_with_quota_retry(
        _llm(temperature=0), SOLVE_PROMPT.format(soru=soru, secenekler=sec_metni)
    )
    if str(cozucu.get("cevap", "")).strip().upper() != dogru:
        return None
    return {
        "konu": topic,
        "soru": soru,
        "secenekler": json.dumps(dict(sorted(secenekler.items())), ensure_ascii=False),
        "dogru": dogru,
        "cozum": " ".join(str(uretim.get("cozum", "")).split()),
    }


def main() -> None:
    if not settings.google_api_key:
        raise SystemExit("GOOGLE_API_KEY tanımlı değil (.env).")

    args = sys.argv[1:]
    n_per_topic = int(args[0]) if args and args[0].isdigit() else 12
    only_topic = " ".join(args[1:]) if len(args) > 1 else None

    topics = math_topics()
    if only_topic:
        if only_topic not in topics:
            raise SystemExit(f"Konu listede yok: {only_topic}")
        topics = [only_topic]

    existing = load_existing()
    is_new = not OUT_CSV.exists()
    out = OUT_CSV.open("a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    if is_new:
        writer.writeheader()

    for topic in topics:
        have = existing.setdefault(topic, [])
        need = n_per_topic - len(have)
        if need <= 0:
            continue
        print(f"{topic}: {len(have)} var, {need} üretilecek", flush=True)
        attempts = 0
        while need > 0 and attempts < n_per_topic * 3:
            attempts += 1
            row = generate_one(topic, have)
            time.sleep(SLEEP_SECONDS)
            if row is None:
                continue
            writer.writerow(row)
            out.flush()
            have.append(row["soru"])
            need -= 1
            print(f"  ✓ {row['soru'][:70]}...", flush=True)
        if need > 0:
            print(f"  UYARI: {topic} için {need} soru eksik kaldı (doğrulama eledi)", flush=True)

    out.close()
    total = sum(len(v) for v in load_existing().values())
    print(f"\nToplam doğrulanmış soru: {total}  →  {OUT_CSV}")


if __name__ == "__main__":
    main()
