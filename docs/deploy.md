# Canlıya Alma - Sprint 3

Bu kurulumda arayüz Streamlit Community Cloud'da, FastAPI ise Railway'de çalışır.
Koç hafızası ve uygulama SQLite veritabanı Railway volume altında tutulur.

## 1. API - Railway

1. Railway'de **New Project > Deploy from GitHub repo** ile bu repoyu seçin.
2. `railway.json` başlangıç komutunu ve `/health` kontrolünü otomatik tanımlar.
3. Servise bir **Volume** ekleyin ve mount path'i tam olarak `/data` yapın.
4. Variables bölümüne şunları ekleyin:

```text
GOOGLE_API_KEY=<Google AI Studio anahtarı>
DATABASE_URL=sqlite:////data/carpan.db
COACH_MEMORY_PATH=/data/coach-checkpoints.sqlite3
LANGGRAPH_STRICT_MSGPACK=true
```

5. Networking bölümünden public domain üretin.
6. `https://<domain>/health` adresinin `status: ok` döndürdüğünü doğrulayın.

> Volume bağlanmazsa dosyalar container dosya sisteminde kalır ve deploy/restart sonrası
> silinebilir. Kalıcı hafıza kabul testi için `/data` volume zorunludur.

## 2. Arayüz - Streamlit Community Cloud

1. `share.streamlit.io` üzerinde **Create app** seçin.
2. Repo/branch'i ve giriş dosyası olarak `frontend/streamlit_app.py` yolunu seçin.
3. Advanced settings içinde Python `3.11` seçin.
4. Secrets alanına şunu ekleyin:

```toml
CARPAN_API_URL = "https://<railway-domain>"
```

5. Deploy edin ve oluşan `streamlit.app` adresini README'nin en üstündeki canlı URL
   bölümüne yazın.

## 3. Kalıcı hafıza kabul testi

1. Uygulamada bir öğrenci oluşturun.
2. Koç sohbetinde: `Bugün rasyonel sayılara çalıştık.` yazın.
3. Railway servisinde **Restart** veya yeni bir deploy gerçekleştirin.
4. Aynı öğrenciyle: `Dün hangi konuya çalışmıştık?` yazın.
5. Yanıtın önceki konuyu kullanmasını doğrulayın.

LLM kullanmadan altyapı doğrulaması:

```bash
python backend/scripts/verify_coach_memory.py
pytest backend/tests/test_persistent_memory.py -q
```

## 4. Uçtan uca telefon testi

Wi-Fi'ı kapatıp mobil veriyle şu akışı deneyin:

`fotoğraf yükle -> anlatım -> mini quiz -> ustalık haritası -> haftalık plan -> koç sohbeti`

## 5. Video öncesi bilinen noktalar

- Railway ücretsiz kaynak limiti nedeniyle ilk istek soğuk başlayabilir.
- Streamlit yükleme limiti `.streamlit/config.toml` içinde 10 MB'dır.
- SQLite tek servis örneği için uygundur; volume bağlı servis yatay çoğaltılmamalıdır.
- `GOOGLE_API_KEY`, `.env` veya `secrets.toml` hiçbir zaman repoya eklenmemelidir.
