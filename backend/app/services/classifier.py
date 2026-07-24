"""T6 — yerel konu sınıflandırıcısı.

Kendi eğittiğimiz TF-IDF + Lojistik Regresyon modeli (bkz.
docs/siniflandirici-karsilastirma.md). API anahtarı ve internet gerektirmez;
GOOGLE_API_KEY yokken yazılı soruların konu etiketlemesi bu modelle yapılır ve
zayıflık haritası anahtarsız da işlemeye devam eder (demo modu).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "konu_siniflandirici.joblib"


@lru_cache(maxsize=1)
def _model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def classify_topic(text: str | None) -> str | None:
    """Metni 27 konuluk TYT Matematik taksonomisinden bir konuya etiketler.

    Model dosyası yoksa ya da metin boşsa None döner (çağıran taraf 503'e düşer).
    """
    if not text or not text.strip():
        return None
    model = _model()
    if model is None:
        return None
    return str(model.predict([text.strip()])[0])
