# Sprint 2 — Takım 76 (Çarpan)

**Sprint Tarihleri:** 6 – 19 Temmuz 2026

---

## Sprint 2 Tamamlanan İşler

### ✅ Kurulum & Demo
- Python sanal ortamı (`python3 -m venv .venv`) ve tüm bağımlılıklar kuruldu
- `.env` dosyası oluşturuldu (GOOGLE_API_KEY ucu açık bırakıldı, anahtar eklendikçe AI özellikleri devreye girer)
- `backend/scripts/seed_demo.py` ile demo verisi yüklendi: **46 sinyal, 4 deneme**
- API: `uvicorn app.main:app --app-dir backend --reload`
- Arayüz (telefon erişimi): `streamlit run frontend/streamlit_app.py --server.address 0.0.0.0`

---

### ✅ Quiz Arayüzü (T3)
- **Yeni backend:** `backend/app/agents/quiz.py` — Gemini ile 4 şıklı quiz sorusu üretimi
- **Yeni endpoint:** `GET /students/{id}/quiz?topic=...` — konu bazlı soru üretir; API key yoksa konu-spesifik fallback döner (arayüz her koşulda çalışır)
- **Yeni endpoint:** `POST /students/{id}/quiz/answer` — cevabı haritaya işler (succeeded=True/False)
- **Frontend:** "Soru Sor" sayfasında anlatım sonrası otomatik "🔁 Benzer Soru — Mini Quiz" bölümü açılır; doğru/yanlış feedback ile ustalık haritası güncellenir

---

### ✅ Analiz Panosu Cilası
- **Konu Ustalık Haritası:** Dikey bar → **yatay bar** + kırmızı→sarı→yeşil renk gradyanı; tooltip'e geçildi
- **Net Gidişatı:** Toplam TYT + **hangi ders veritabanında varsa o dersin ayrı çizgisi** (hardcoded ders ismi yok)
  - `GET /students/{id}/subject_trend` yeni endpoint → `load_subject_nets` fonksiyonu
- **Haftalık Plan:** Analiz Panosu'nda `📅 Haftalık Çalışma Planı` expander — "Plan Oluştur" butonu koçu çağırır, API key yoksa yönlendirme mesajı gösterir
- **Öncelikli Konular tablosu:** Ustalık ve öncelik formatlanarak gösteriliyor

---

### ✅ Mobil UX İyileştirmeleri
- `initial_sidebar_state="collapsed"` → mobilde başta sidebar kapalı
- Tüm butonlar `use_container_width=True` ile tam genişlik
- Soru geçmişi tablosu: 5 sütun → 3 sütun (Tarih, Konu, Başarılı)
- Tablo `use_container_width=True` → yatay kaydırma azaldı
- Minimal CSS: geniş butonlar, büyük radio şıkları (quiz için)
- API key yokken kullanıcı dostu mesaj + aistudio.google.com linki

---

## Ürün Durumu — Ekran Görüntüleri

### 📸 Soru Sor
![Sprint 2 — Soru Sor](sprint2_soru_sor.png)

### 📝 Deneme Netleri
![Sprint 2 — Deneme Netleri](sprint2_deneme_netleri.png)

### 📊 Analiz Panosu — Ustalık Haritası
![Sprint 2 — Analiz Panosu](sprint2_analiz_panosu.png)

### 📈 Analiz Panosu — Ders Bazlı Net Gidişatı
![Sprint 2 — Net Gidişatı](sprint2_net_gidisati.png)

### 💬 Koç Sohbeti
![Sprint 2 — Koç Sohbeti](sprint2_koc_sohbeti.png)

---

## Sprint 2 Board

[Miro Backlog Board](https://miro.com/app/board/uXjVH-ttQY8=/?share_link_id=525660778806)

---

## Sprint Review

**Tamamlanan:**
- Quiz akışı uçtan uca çalışıyor (soru üret → cevapla → haritaya işle)
- Ders bazlı net gidişatı (Türkçe, Matematik, Fen, Sosyal ayrı çizgiler)
- Haftalık plan görünümü (koç sohbetiyle entegre)
- Mobil UX iyileştirmeleri

**Kararlar:**
- GOOGLE_API_KEY olmadan ürün demo modunda çalışmaya devam eder (fallback quiz soruları)
- Subject trend endpoint generic yazıldı — ilerleyen sprintlerde yeni ders eklenmesi halinde kod değişmez

## Sprint Retrospective

- API key olmadan ürünün "demo modu"nun olması jüri sunumu için kritik — bu özellik Sprint 2'de hayata geçti
- Streamlit'in mobil deneyimi sınırlı; Sprint 3'te PWA ya da farklı frontend framework değerlendirilebilir
- Quiz soru kalitesi (AI üretimi vs fallback) Sprint 3 T4'te ÖSYM setli değerlendirmeyle ölçülecek

---

## Sprint 3'e Devredilen

- RAG (Chroma + kazanım dokümanları) — B4
- Kendi konu sınıflandırıcısını eğit (embedding + ML) — T6
- GradientBoosting net tahmin modeli — A5
- SQLite kalıcı koç hafızası — B5
- Deneme karnesi fotoğrafından net okuma — T5
