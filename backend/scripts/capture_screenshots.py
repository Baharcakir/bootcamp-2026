"""Ürün ekran görüntülerini otomatik çeker (sprint raporları ve demo malzemesi için).

Kullanım (API 8000 ve Streamlit 8501 portlarında çalışırken, repo kökünden):
    python backend/scripts/capture_screenshots.py [hedef_klasor]

Sistem Chrome'unu kullanır (playwright, channel="chrome" — ek tarayıcı indirmez).
Streamlit sayfaları ?page=N derin bağlantısıyla açılır; websocket render'ı için bekler.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_OUT = Path("ProjectManagement/Sprint2/screenshots")
UI = "http://localhost:8501"
API_DOCS = "http://localhost:8000/docs"
PAGES = [
    (0, "soru-sor"),
    (1, "deneme-netleri"),
    (2, "analiz-panosu"),
    (3, "haftalik-plan"),
]
RENDER_WAIT_MS = 7000  # Streamlit websocket + Plotly çizimi için nefes payı


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for index, name in PAGES:
            page.goto(f"{UI}/?page={index}")
            page.wait_for_timeout(RENDER_WAIT_MS)
            path = out / f"urun-{index + 1}-{name}.png"
            page.screenshot(path=str(path), full_page=True)
            print(f"✓ {path.name}")

        page.goto(API_DOCS)
        page.wait_for_timeout(3000)
        page.screenshot(path=str(out / "api-docs.png"), full_page=True)
        print("✓ api-docs.png")
        browser.close()
    print(f"\nGörüntüler: {out}")


if __name__ == "__main__":
    main()
