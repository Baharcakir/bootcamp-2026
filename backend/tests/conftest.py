import os
import sys
from pathlib import Path

# Testler dosya tabanlı DB oluşturmasın: lifespan'daki create_all geçici in-memory DB'ye gitsin.
# (Test verisi zaten fixture'daki override edilmiş oturumdan gelir.)
os.environ["DATABASE_URL"] = "sqlite://"

# `app` paketini import edilebilir yap (repo kökünden `pytest backend/tests` ile çalışır).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
