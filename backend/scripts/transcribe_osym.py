"""T6 — ÖSYM matematik sorularını sayfa görüntülerinden metne çevirir ve ön-etiketler.

Kendi konu sınıflandırıcımız metin üzerinden çalışacak; bu script her sorunun metnini
Gemini Vision ile çıkarır ve 27 konuluk taksonomiden bir ön-etiket önerir.

- 2018-2023: eğitim adayı — ön-etiketler İNSAN ONAYINDAN geçmeden eğitimde kullanılmaz
  (bkz. docs/mimari.md "Veri Protokolü").
- 2024-2026: yalnız metin için — etiketleri data/osym/etiketleme.csv'deki nihai insan
  etiketleridir; buradaki ön-etiket sütunu 2024-2026 için YOK SAYILIR.

Çıktı: data/osym/raw/sorular_metin.csv  (ÖSYM metni telif nedeniyle yerel kalır;
raw/ klasörü gitignore'dadır — repoya yalnız türetilmiş model/metrikler gider.)

Çalıştırma (repo kökünden, .env'de GOOGLE_API_KEY ile):
    python backend/scripts/transcribe_osym.py 2018            # tek yıl (pilot)
    python backend/scripts/transcribe_osym.py                 # kalan tüm yıllar

Kaldığı yerden devam eder: CSV'de kaydı olan sayfalar atlanır.
"""

from __future__ import annotations

import base64
import csv
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_google_genai import ChatGoogleGenerativeAI  # noqa: E402

from app.agents.tutor import LABELING_RULES  # noqa: E402
from app.agents.utils import content_to_text  # noqa: E402
from app.config import settings  # noqa: E402
from app.services.queries import load_topics  # noqa: E402

RAW_DIR = ROOT / "data" / "osym" / "raw"
OUT_CSV = RAW_DIR / "sorular_metin.csv"
FIELDS = ["kitapcik", "soru_no", "metin", "on_konu", "emin", "kaynak_sayfa"]
SLEEP_SECONDS = 4  # ücretsiz kota (dakikalık istek limiti) için nefes payı

PAGE_PROMPT = """Bu görüntü, ÖSYM TYT Temel Matematik Testi kitapçığından bir sayfadır.
Sayfada TAMAMI görünen her soru için üç şey üret: numara, soru metni, konu.

Metin kuralları:
- Soru gövdesini olduğu gibi Türkçe yaz; matematiksel ifadeleri düz metinle göster
  (ör. x^2, 3/4, √5, |x|). Cevap şıklarını (A-E) YAZMA.
- Soruda şekil/grafik/tablo varsa metnin uygun yerine [ŞEKİL], [GRAFİK] veya [TABLO] yaz.
- Bir kısmı önceki/sonraki sayfada kalan soruları DAHİL ETME.

Konu listesi (yalnızca bunlardan seç, adları AYNEN yaz):
{topics}

{rules}

Konudan emin değilsen "emin" alanını false yap.

Cevabını SADECE şu JSON biçiminde ver, başka hiçbir şey yazma:
[{{"no": 12, "metin": "...", "konu": "Problemler", "emin": true}}]"""


def math_topics() -> list[str]:
    data = load_topics()
    return next(s["topics"] for s in data["subjects"] if s["name"] == "Matematik")


def parse_json_array(reply: str) -> list[dict]:
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    rows = []
    for item in data:
        try:
            rows.append({
                "no": int(item["no"]),
                "metin": " ".join(str(item["metin"]).split()),
                "konu": str(item["konu"]).strip(),
                "emin": bool(item.get("emin", True)),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def transcribe_page(llm: ChatGoogleGenerativeAI, png: Path, topics_text: str) -> list[dict]:
    data_uri = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
    message = HumanMessage(
        content=[
            {"type": "text", "text": PAGE_PROMPT.format(topics=topics_text, rules=LABELING_RULES)},
            {"type": "image_url", "image_url": {"url": data_uri}},
        ]
    )
    reply = llm.invoke([message]).content
    return parse_json_array(content_to_text(reply))


def load_existing() -> tuple[list[dict], set[str], set[tuple[str, int]]]:
    if not OUT_CSV.exists():
        return [], set(), set()
    rows = list(csv.DictReader(OUT_CSV.open(encoding="utf-8")))
    done_pages = {r["kaynak_sayfa"] for r in rows}
    done_questions = {(r["kitapcik"], int(r["soru_no"])) for r in rows}
    return rows, done_pages, done_questions


def main() -> None:
    if not settings.google_api_key:
        raise SystemExit("GOOGLE_API_KEY tanımlı değil (.env).")

    years = [a for a in sys.argv[1:] if a.isdigit()]
    if not years:
        years = sorted(d.name for d in RAW_DIR.iterdir() if d.is_dir() and d.name.isdigit())

    topics = set(math_topics())
    topics_text = ", ".join(sorted(topics))
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model, google_api_key=settings.google_api_key, temperature=0
    )

    rows, done_pages, done_questions = load_existing()
    is_new = not OUT_CSV.exists()
    out = OUT_CSV.open("a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    if is_new:
        writer.writeheader()

    for year in years:
        pages = sorted(
            (RAW_DIR / year).glob("mat-*.png"),
            key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
        )
        if not pages:
            print(f"UYARI: {year} için sayfa görüntüsü yok")
            continue
        for png in pages:
            page_key = f"{year}/{png.name}"
            if page_key in done_pages:
                continue
            page_rows = transcribe_page(llm, png, topics_text)
            new_count = 0
            for item in page_rows:
                key = (year, item["no"])
                if key in done_questions:  # sayfa taşmalarına karşı ilk görüş kazanır
                    continue
                done_questions.add(key)
                bad_topic = item["konu"] not in topics
                writer.writerow({
                    "kitapcik": year,
                    "soru_no": item["no"],
                    "metin": item["metin"],
                    "on_konu": item["konu"],
                    # listede olmayan konu adı üretildiyse onaya düşsün
                    "emin": "" if bad_topic else ("evet" if item["emin"] else "hayir"),
                    "kaynak_sayfa": page_key,
                })
                new_count += 1
            done_pages.add(page_key)
            out.flush()
            print(f"  {page_key}: {new_count} soru", flush=True)
            time.sleep(SLEEP_SECONDS)

    out.close()

    # Özet: yıl başına soru sayısı (TYT matematik = 40 beklenir)
    all_rows, _, _ = load_existing()
    counts: dict[str, int] = {}
    for r in all_rows:
        counts[r["kitapcik"]] = counts.get(r["kitapcik"], 0) + 1
    print("\nToplam:")
    for year in sorted(counts):
        flag = "" if counts[year] == 40 else "  ← 40 DEĞİL, kontrol et"
        print(f"  {year}: {counts[year]} soru{flag}")
    print(f"\nÇıktı: {OUT_CSV}")


if __name__ == "__main__":
    main()
