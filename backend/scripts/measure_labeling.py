"""T4 — Otomatik konu etiketlemenin doğruluğunu ÖSYM değerlendirme setinde ölçer.

Akış: her kitapçığın matematik sayfası görüntüleri (data/osym/raw/<yıl>/mat-*.png) sırayla
Gemini'ye gönderilir; sayfadaki tamamı görünen soruların {soru_no: konu} etiketleri istenir.
Model etiketleri, elle yapılmış etiketlerle (data/osym/etiketleme.csv) karşılaştırılır.

Çıktılar:
- docs/etiketleme-dogruluk-raporu.md  (doğruluk tabloları + uyuşmazlıklar + yöntem)
- data/osym/uyusmazliklar.csv         (denetim turu listesi)

Çalıştırma (repo kökünden, .env'de GOOGLE_API_KEY ile):
    python backend/scripts/measure_labeling.py

Not: ~36 Gemini çağrısı yapar; ücretsiz kota dostu olması için çağrılar arasında bekler.
"""

from __future__ import annotations

import base64
import csv
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_google_genai import ChatGoogleGenerativeAI  # noqa: E402

from app.config import settings  # noqa: E402
from app.services.queries import load_topics  # noqa: E402

RAW_DIR = ROOT / "data" / "osym" / "raw"
LABELS_CSV = ROOT / "data" / "osym" / "etiketleme.csv"
REPORT_MD = ROOT / "docs" / "etiketleme-dogruluk-raporu.md"
MISMATCH_CSV = ROOT / "data" / "osym" / "uyusmazliklar.csv"
SLEEP_SECONDS = 4  # ücretsiz kota (dakikalık istek limiti) için nefes payı

PAGE_PROMPT = """Bu görüntü, ÖSYM TYT Temel Matematik Testi kitapçığından bir sayfadır.
Sayfada TAMAMI görünen her sorunun numarasını ve konusunu belirle.

Konu listesi (yalnızca bunlardan seç, adları AYNEN yaz):
{topics}

Kurallar:
- Soru numarası, sayfada sorunun başında yazan numaradır.
- Bir kısmı önceki/sonraki sayfada kalan soruları DAHİL ETME.
- Her soru için listeden TAM olarak bir konu seç; listede olmayan ad uydurma.

Cevabını SADECE şu JSON biçiminde ver, başka hiçbir şey yazma:
{{"12": "Problemler", "13": "Kümeler"}}"""


def math_topics() -> list[str]:
    data = load_topics()
    return next(s["topics"] for s in data["subjects"] if s["name"] == "Matematik")


def load_human_labels() -> dict[tuple[str, int], dict]:
    rows = list(csv.DictReader(LABELS_CSV.open(encoding="utf-8-sig")))
    return {
        (r["kitapcik"], int(r["soru_no"])): {"konu": r["konu"].strip(), "not": (r["not"] or "").strip()}
        for r in rows
        if (r["konu"] or "").strip()
    }


def parse_json_reply(reply: str) -> dict[str, str]:
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    return {str(k): str(v).strip() for k, v in data.items() if str(k).strip().isdigit()}


def label_page(llm: ChatGoogleGenerativeAI, png: Path, topics_text: str) -> dict[str, str]:
    data_uri = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
    message = HumanMessage(
        content=[
            {"type": "text", "text": PAGE_PROMPT.format(topics=topics_text)},
            {"type": "image_url", "image_url": {"url": data_uri}},
        ]
    )
    reply = llm.invoke([message]).content
    return parse_json_reply(reply if isinstance(reply, str) else str(reply))


def measure() -> None:
    if not settings.google_api_key:
        raise SystemExit("GOOGLE_API_KEY tanımlı değil (.env).")

    topics = math_topics()
    topics_text = ", ".join(topics)
    human = load_human_labels()
    booklets = sorted({k for k, _ in human})

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model, google_api_key=settings.google_api_key, temperature=0
    )

    model_labels: dict[tuple[str, int], str] = {}
    call_count = 0
    for booklet in booklets:
        pages = sorted(
            (RAW_DIR / booklet).glob("mat-*.png"),
            key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)),
        )
        if not pages:
            print(f"UYARI: {booklet} için sayfa görüntüsü yok ({RAW_DIR / booklet})")
            continue
        for png in pages:
            call_count += 1
            page_result = label_page(llm, png, topics_text)
            for qno_str, konu in page_result.items():
                key = (booklet, int(qno_str))
                if key not in model_labels:  # ilk görüş kazanır (sayfa taşmalarına karşı)
                    model_labels[key] = konu
            print(f"  {booklet}/{png.name}: {len(page_result)} soru etiketlendi")
            time.sleep(SLEEP_SECONDS)

    # Karşılaştırma
    compared, mismatches, missing = [], [], []
    for key, h in sorted(human.items()):
        m = model_labels.get(key)
        if m is None:
            missing.append(key)
            continue
        ok = m == h["konu"]
        compared.append((key, h, m, ok))
        if not ok:
            mismatches.append((key, h, m))

    total = len(compared)
    correct = sum(1 for *_, ok in compared if ok)
    accuracy = correct / total if total else 0.0

    per_booklet = {}
    for booklet in booklets:
        rows = [c for c in compared if c[0][0] == booklet]
        oks = sum(1 for *_, ok in rows if ok)
        per_booklet[booklet] = (oks, len(rows))

    confusion = Counter((h["konu"], m) for _, h, m in mismatches)

    # Uyuşmazlık CSV (denetim turu girdisi)
    with MISMATCH_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["kitapcik", "soru_no", "insan_konu", "model_konu", "insan_notu"])
        for (booklet, qno), h, m in mismatches:
            writer.writerow([booklet, qno, h["konu"], m, h["not"]])

    # Rapor
    lines = [
        "# T4 — Otomatik Konu Etiketleme Doğruluk Raporu (ilk ölçüm)",
        "",
        "**Yöntem:** Değerlendirme seti, 2024-2026 ÖSYM TYT kitapçıklarının 120 matematik sorusudur.",
        "Etiketler tek etiketçi + kararsızlık işaretleme yöntemiyle elle atandı (43 soru işaretli).",
        f"Otomatik etiketleme: {settings.gemini_model} modeline sayfa görüntüleri verildi (sıcaklık 0,",
        f"{call_count} çağrı); model, sayfadaki soruları 27 konuluk taksonomiden etiketledi.",
        "Bu ilk ölçümdür — uyuşmazlık denetimi (aşağıdaki liste + işaretli sorular) sonrası",
        "nihai etiketlerle rapor güncellenecektir.",
        "",
        "## Sonuçlar",
        "",
        "| Metrik | Değer |",
        "|---|---|",
        f"| Karşılaştırılan soru | {total}/120 |",
        f"| Model etiketi eksik | {len(missing)} |",
        f"| **Doğruluk (ilk ölçüm)** | **{correct}/{total} = %{accuracy * 100:.1f}** |",
        "",
        "| Kitapçık | Doğruluk |",
        "|---|---|",
    ]
    for booklet, (oks, n) in per_booklet.items():
        pct = oks / n * 100 if n else 0
        lines.append(f"| {booklet} | {oks}/{n} (%{pct:.1f}) |")

    lines += ["", f"## Uyuşmazlıklar ({len(mismatches)} soru — denetim turu listesi)", "",
              "| Kitapçık | Soru | İnsan | Model | İnsan notu |", "|---|---|---|---|---|"]
    for (booklet, qno), h, m in mismatches:
        note = h["not"][:60].replace("|", "/")
        lines.append(f"| {booklet} | {qno} | {h['konu']} | {m} | {note} |")

    if missing:
        lines += ["", "## Model etiketi eksik kalan sorular", ""]
        lines.append(", ".join(f"{b} s.{q}" for b, q in missing))

    if confusion:
        lines += ["", "## En sık karışan konu çiftleri (insan → model)", ""]
        for (h_konu, m_konu), n in confusion.most_common(8):
            lines.append(f"- {h_konu} → {m_konu}: {n}")

    lines += [
        "",
        "## Notlar",
        "",
        "- Polinomlar, Çarpanlara Ayırma ve Üçgenin Yardımcı Elemanları 2024-2026 setinde hiç",
        "  görülmedi; bu konularda ölçüm yapılamadı.",
        "- Sonraki adım: uyuşmazlık denetimi → `nihai_konu` doldurulur → rapor nihai sayılarla",
        "  güncellenir; aynı set T6'da kendi sınıflandırıcımızla karşılaştırma için kullanılır.",
        "",
        f"*Denetim listesi: `data/osym/uyusmazliklar.csv` ({len(mismatches)} satır)*",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nDoğruluk: {correct}/{total} = %{accuracy * 100:.1f} | eksik: {len(missing)}")
    print(f"Rapor: {REPORT_MD}")
    print(f"Denetim listesi: {MISMATCH_CSV}")


if __name__ == "__main__":
    measure()
