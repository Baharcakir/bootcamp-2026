"""ÖSYM çıkmış TYT kitapçıklarından T4 etiketleme setini hazırlar.

Ne yapar:
1. `data/osym/raw/` altındaki kitapçık PDF'lerinde Temel Matematik bölümünü otomatik bulur
   (ilk "MATEMATİK TESTİ" sayfasından ilk "FEN BİLİMLERİ TESTİ" sayfasının öncesine kadar),
2. O sayfaları PNG'ye çevirir (etiketçiler ve Gemini ölçümü bu görüntüleri kullanır),
3. `data/osym/etiketleme.csv` dosyasına kitapçık başına 40 soru satırı ekler
   (iki bağımsız etiketçi sütunu + nihai karar + not).

Telif notu: PDF ve PNG'ler repoya GİRMEZ (data/osym/raw gitignore'da); yalnızca etiketler
(yıl + soru no + konu adı) paylaşılır. Çalıştırma:

    python backend/scripts/prepare_osym_eval.py

Gereksinim: poppler (pdftotext/pdftoppm) — macOS: brew install poppler
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "osym" / "raw"
CSV_PATH = ROOT / "data" / "osym" / "etiketleme.csv"
QUESTIONS_PER_BOOKLET = 40
RENDER_DPI = 150

MAT_RE = re.compile(r"MATEMAT[İI]K\s*TEST", re.IGNORECASE)
FEN_RE = re.compile(r"FEN\s*B[İI]L[İI]MLER[İI]\s*TEST", re.IGNORECASE)
YEAR_RE = re.compile(r"(20\d{2})")

CSV_FIELDS = ["kitapcik", "soru_no", "konu", "nihai_konu", "not"]


def page_texts(pdf: Path) -> list[str]:
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout
    return out.split("\f")


def find_math_range(pdf: Path) -> tuple[int, int]:
    """Matematik bölümünün (başlangıç, bitiş) sayfa numaralarını (1 tabanlı) döndürür.

    ÖSYM düzeni: sosyal bölümünün SON sayfasında "...MATEMATİK TESTİNE GEÇİNİZ" yazar
    (ilk eşleşme odur, matematik değildir); matematiğin SON sayfasında ise
    "...FEN BİLİMLERİ TESTİNE GEÇİNİZ" yazar (ilk FEN eşleşmesi matematiğe dahildir).
    """
    pages = page_texts(pdf)
    mat_hits = [i + 1 for i, p in enumerate(pages) if MAT_RE.search(p)]
    fen_hits = [i + 1 for i, p in enumerate(pages) if FEN_RE.search(p)]
    if not mat_hits or not fen_hits:
        raise RuntimeError(f"{pdf.name}: matematik bölümü otomatik bulunamadı — elle kontrol et")

    # "GEÇİNİZ" sayfasını atla: ilk iki eşleşme ardışıksa gerçek başlangıç ikincisidir
    start = mat_hits[1] if len(mat_hits) > 1 and mat_hits[1] == mat_hits[0] + 1 else mat_hits[0]
    # İlk FEN eşleşmesi aynı zamanda MATEMATİK de içeriyorsa ("MATEMATİK TESTİ BİTTİ")
    # o sayfa matematiğin son sayfasıdır; içermiyorsa fen başlığıdır, öncesinde bitmiştir.
    fen_first = fen_hits[0]
    end = fen_first if MAT_RE.search(pages[fen_first - 1]) else fen_first - 1
    if not (start < end):
        raise RuntimeError(f"{pdf.name}: aralık tutarsız (sf {start}-{end}) — elle kontrol et")
    return start, end


def render_pages(pdf: Path, start: int, end: int, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(RENDER_DPI), "-f", str(start), "-l", str(end),
         str(pdf), str(out_dir / "mat")],
        check=True,
    )
    return len(list(out_dir.glob("mat-*.png")))


def load_existing_booklets() -> set[str]:
    if not CSV_PATH.exists():
        return set()
    with CSV_PATH.open(encoding="utf-8") as f:
        return {row["kitapcik"] for row in csv.DictReader(f)}


def append_rows(booklet: str) -> None:
    new_file = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if new_file:
            writer.writeheader()
        for q in range(1, QUESTIONS_PER_BOOKLET + 1):
            writer.writerow({"kitapcik": booklet, "soru_no": q,
                             "konu": "", "nihai_konu": "", "not": ""})


def main() -> None:
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"PDF bulunamadı: {RAW_DIR} altına kitapçıkları koyun.")
        return
    existing = load_existing_booklets()
    for pdf in pdfs:
        year_match = YEAR_RE.search(pdf.name)
        booklet = year_match.group(1) if year_match else pdf.stem
        start, end = find_math_range(pdf)
        count = render_pages(pdf, start, end, RAW_DIR / booklet)
        if booklet in existing:
            status = "CSV'de zaten var, satır eklenmedi"
        else:
            append_rows(booklet)
            status = f"{QUESTIONS_PER_BOOKLET} etiket satırı eklendi"
        print(f"✓ {booklet}: matematik sf {start}-{end} → {count} görüntü | {status}")
    print(f"\nEtiket dosyası: {CSV_PATH}")
    print("Yönerge: docs/etiketleme-yonergesi.md")


if __name__ == "__main__":
    main()
