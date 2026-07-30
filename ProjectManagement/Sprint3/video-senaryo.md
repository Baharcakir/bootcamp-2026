# 🎬 Video Senaryosu — Çarpan (3 dakika)

**Hedef:** Jüri önünde 3 dakikada değer önerisini + AI kanıtlarını + canlı demoyu göster.  
**Format:** Ekran kaydı (canlı URL üzerinden) + gerçek telefon fotoğraf çekimi sahnesi.  
**Ses:** Türkçe anlatım + ekran paylaşımı.

---

## ⏱️ Sahne Planı

### 0:00 – 0:30 | Sorun (Problem Frame)

**Ne gösterilir:** Siyah/koyu arka plan, minimal metin overlay  
**Anlatım:**
> "YKS'ye hazırlanan öğrencilerin %80'i hangi konulardan zayıf olduğunu bilmiyor.
> Soru çözüm uygulamaları sadece anlatır — öğrenciyi tanımaz.
> Koçluk pahalıdır. 'Analiz' araçları form doldurtur — kimse doldurmaz."

**Geçiş:** "Biz farklı bir şey yaptık."

---

### 0:30 – 1:00 | Çözüm Fikri (Value Proposition)

**Ne gösterilir:** Uygulama ana ekranı (Soru Sor sayfası)  
**Anlatım:**
> "Çarpan'da öğrenci hiç veri girmez.
> Çözemediği matematik sorusunun fotoğrafını atar — sistem anında adım adım anlatır
> ve soruyu otomatik konu etiketleyerek zayıflık haritasını kendiliğinden örüyor."

**Anahtar mesaj:** *Analitik, kullanımın yan ürünüdür.*

---

### 1:00 – 2:15 | Canlı Demo (Live Demo)

#### 1:00 – 1:35 — Soru Sor → Anlatım → Harita

**Akış:**
1. Telefon kamerası sahnesi: gerçek TYT sorusu kağıda fotoğraf çekiliyor
2. Fotoğraf uygulamaya yükleniyor (ya da kamera input kullanılıyor)
3. "🧑‍🏫 Anlat" butonuna basılıyor
4. Spinner → **anlatım ekranda beliriyor**
5. `🏷️ Matematik / Problemler olarak haritana işlendi` mesajı gösteriliyor
6. Mini Quiz açılıyor → şık seçiliyor → "✅ Doğru! Ustalık haritana işlendi."

**Anlatım:**
> "Fotoğraf yüklüyorum — yapay zeka adım adım anlatıyor ve konuyu otomatik etiketliyor.
> Anlatım bitti, hemen benzer soru geliyor — doğru cevaplıyorum, harita güncelleniyor."

#### 1:35 – 1:55 — Analiz Panosu

**Akış:**
1. Analiz Panosu sayfasına geçiş
2. Renkli ustalık haritası (kırmızı → sarı → yeşil) gösteriliyor
3. ⭐ Tahmin yıldızı üzerine hover

**Anlatım:**
> "Ustalık haritası — kırmızı konulardan zayıf, yeşil güçlü.
> Yıldız işareti bir sonraki deneme için tahminimiz."

#### 1:55 – 2:15 — Haftalık Plan + Koç

**Akış:**
1. Haftalık Plan sayfası → "✨ Bu haftanın planını oluştur" → plan tablosu
2. Koç Sohbeti sayfası → "Nerelerde zayıfım?" → koç yanıtı

**Anlatım:**
> "Sınav tarihim ve saat bütçem sisteme tanımlı — kişisel haftalık plan otomatik çıkıyor.
> Koça soruyorum: 'Nerelerde zayıfım?' — öğrencimi tanıyan, verilere dayalı cevap alıyorum."

---

### 2:15 – 2:45 | AI Kanıtları (AI Evidence)

**Ne gösterilir:** Ekranda rapor sayfaları / kod / metrikler  
**Anlatım:**

> "Şimdi biraz teknik detay."

**Gösterilecekler (slayt değil — ekranda gerçek belgeler):**

1. **%83.3 doğruluk** → `docs/etiketleme-dogruluk-raporu.md` ekranda açık
   > "120 gerçek ÖSYM sorusunda otomatik konu etiketleme %83.3 doğruluk."

2. **Kendi sınıflandırıcımız** → `docs/siniflandirici-karsilastirma.md`
   > "Kendi eğittiğimiz TF-IDF + LogReg modelimiz %58.3 — API key olmadan çalışır,
   > milisaniyede sonuç verir, sıfır maliyet."

3. **Kalibrasyon** → `docs/kalibrasyon.md`
   > "Bayesçi ustalık modeli 1000 sentetik öğrenciyle kalibre edildi: MAE %10.2."

4. **Net tahmin** → `docs/net-tahmin.md`
   > "GradientBoosting net tahmin modeli baseline'ı %34 geçti."

5. **Agent mimarisi** → `README.md` mermaid diyagramı
   > "LangGraph süpervizör mimarisi: koç, tutor ve analiz agent'larını orkestre ediyor."

---

### 2:45 – 3:00 | Ekip + Gelecek

**Ne gösterilir:** GitHub repo + takım tablosu  
**Anlatım:**
> "Takım 76 — Bahar, Görkem, Doğa ve Emir Arda.
> Repo: github.com/Baharcakir/bootcamp-2026
> Sonraki adım: gerçek öğrenci pilotu, müfredat genişlemesi (TYT Türkçe, Fen),
> ve B2B — öğretmenlerin sınıflarını takip edeceği panel."

**Kapanış:** Logo + "Çarpan — Önce değer, sonra veri."

---

## 🎬 Çekim Notları

| Sahne | Araç | Not |
|---|---|---|
| Telefon fotoğrafı | Fiziksel telefon | Gerçek kağıt soru + gerçek çekim — slayt değil |
| Ekran kaydı | OBS / QuickTime | `localhost:8501` — canlı URL üzerinden |
| Ses | Mikrofon | Gürültüsüz ortam, sade anlatım |
| Metrikler | Browser | Markdown dosyaları ekranda açık — terminal/IDE değil |
| Kapanış | Ekran | GitHub repo + takım tablosu |

## ⚠️ Çekim Öncesi Kontrol

- [ ] Backend çalışıyor: `uvicorn app.main:app --reload --app-dir backend`
- [ ] Frontend çalışıyor: `streamlit run frontend/streamlit_app.py`
- [ ] Demo öğrencisi var ve ustalık haritasında veri dolu
- [ ] API key `.env` dosyasında tanımlı (Gemini anlatımı için)
- [ ] Ekran çözünürlüğü 1080p+
- [ ] Ses test edildi
- [ ] Yedek: ekran kaydı önceden alındı (canlı demo riskine karşı)
- [ ] Süre prova edildi: **3 dakika aşılmıyor**
