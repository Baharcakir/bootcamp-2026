# GitHub Web Üzerinden Sprint 3 Yükleme

Bu klasördeki dosyaları **repo köküne aynı dizin yollarıyla** yükleyin.
Dışarıdaki `carpan-sprint3-web-yukleme-hazir` klasör adını repoya eklemeyin.

## Yüklenmeyecek dosyalar

- `__pycache__/`
- `*.pyc`
- `.streamlit/secrets.toml`
- `GOOGLE_API_KEY` içeren herhangi bir dosya

## Ayrıca üç mevcut dosyayı GitHub web editöründe düzenleyin

### 1. `frontend/streamlit_app.py`

Şunu bulun:

```python
API_URL = os.getenv("CARPAN_API_URL", "http://localhost:8000")
```

Şununla değiştirin:

```python
def _runtime_setting(name: str, default: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    try:
        return str(st.secrets.get(name, default))
    except FileNotFoundError:
        return default


API_URL = _runtime_setting("CARPAN_API_URL", "http://localhost:8000").rstrip("/")
```

### 2. `.gitignore`

Dosyanın sonuna ekleyin:

```gitignore
# Streamlit yerel sırları
.streamlit/secrets.toml
```

### 3. `README.md`

İlk `---` çizgisinden önce ekleyin ve deploy sonrası URL'leri değiştirin:

```markdown
<!-- SPRINT3_LIVE_URLS -->
## 🌐 Canlı Uygulama

- **Arayüz:** `STREAMLIT_URL_DEPLOY_SONRASI`
- **API sağlık:** https://RAILWAY_URL_DEPLOY_SONRASI/health

> URL'ler deploy tamamlandıktan sonra gerçek adreslerle güncellenmelidir.
```

## Kontrol

Yükleme bittikten sonra Actions sekmesinde CI sonucunu kontrol edin. Yerelde çalıştırabiliyorsanız:

```bash
pip install -r requirements.txt
pytest backend/tests -q
ruff check backend frontend
python backend/scripts/verify_coach_memory.py
```
