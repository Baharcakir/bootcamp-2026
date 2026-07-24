"""LLM cevaplarını düz metne çeviren ortak yardımcı.

Gemini 3 ailesi (gemini-flash-latest) cevabı düz string yerine içerik bloğu listesi
olarak dönebiliyor: [{"type": "text", "text": "...", "extras": {...}}, ...].
str() ile çevirmek Python repr'ini üretip JSON ayrıştırmayı bozduğundan, tüm
.content tüketen yerler bu yardımcıyı kullanır.
"""

from __future__ import annotations


def content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return str(content)
