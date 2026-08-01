# 🎬 Video Senaryosu — Çarpan (3 dakika)

**Hedef:** Jüri önünde 3 dakikada değer önerisini + canlı demoyu + AI kanıtlarını göster.  
**Format:** Ekran kaydı (canlı URL üzerinden) + gerçek telefon fotoğraf çekimi sahnesi.  
**Ses:** Türkçe anlatım + ekran paylaşımı.  
**Canlı adres:** https://carpan-tyt-kocu.streamlit.app/ (açılışta Demo Öğrenci seçili gelir)

---

## ⏱️ Sahne Planı

### 0:00 – 0:25 | Sorun (Problem Frame)

**Ne gösterilir:** Koyu arka plan, minimal metin overlay  
**Anlatım:**
> "YKS'ye hazırlanan bir öğrenci hangi konudan zayıf olduğunu çoğu zaman bilmez.
> Soru çözüm uygulamaları soruyu anlatır ama öğrenciyi tanımaz.
> Koçluk pahalıdır. 'Analiz' araçları ise form doldurtur — kimse doldurmaz."

**Geçiş:** "Biz farklı bir şey yaptık."

> ⚠️ Kaynaksız istatistik kullanma (ör. "öğrencilerin %80'i"). Elimizde böyle bir
> araştırma verisi yok; jüri kaynak sorarsa savunamayız.

---

### 0:25 – 0:45 | Çözüm Fikri (Value Proposition)

**Ne gösterilir:** Uygulama ana ekranı (Soru Sor sayfası)  
**Anlatım:**
> "Çarpan'da öğrenci hiç veri girmez.
> Çözemediği matematik sorusunun fotoğrafını atar — sistem anında adım adım anlatır
> ve soruyu otomatik konu etiketleyerek zayıflık haritasını kendiliğinden örer."

**Anahtar mesaj:** *Analitik, kullanımın yan ürünüdür.*

---

### 0:45 – 2:10 | Canlı Demo (Live Demo)

#### 0:45 – 1:15 — Soru Sor → Anlatım → Etiket → Quiz

**Akış:**
1. Telefon kamerası sahnesi: gerçek TYT sorusu kağıda fotoğraf çekiliyor
2. Fotoğraf uygulamaya yükleniyor
3. "🧑‍🏫 Anlat" butonuna basılıyor
4. Spinner → **anlatım ekranda beliriyor** + MEB kazanımı kaynağı + benzer çıkmış sorular
5. `🏷️ Matematik / … olarak haritana işlendi` mesajı gösteriliyor
6. Mini Quiz açılıyor → şık seçiliyor → "✅ Doğru! Ustalık haritana işlendi."

**Anlatım:**
> "Fotoğraf yüklüyorum — yapay zeka adım adım anlatıyor, konuyu otomatik etiketliyor
> ve müfredat kazanımını kaynak gösteriyor. Hemen ardından benzer soru geliyor;
> doğru cevaplıyorum, harita güncelleniyor."

#### 1:15 – 1:30 — Karne Fotoğrafından Net Okuma (T5)

**Akış:**
1. Deneme Netleri sayfası
2. Gerçek bir deneme karnesi fotoğrafı yükleniyor
3. Ders bazlı doğru/yanlış/boş sayıları **otomatik dolduruluyor**, öğrenci onaylıyor

**Anlatım:**
> "Deneme netlerini elle girmek zorunda da değil — karnesinin fotoğrafını atıyor,
> netler kendiliğinden okunuyor. Öğrenci hiçbir yere veri girmiyor."

#### 1:30 – 1:50 — Analiz Panosu

**Akış:**
1. Analiz Panosu sayfası
2. Renkli ustalık haritası (kırmızı → yeşil), güven aralıklarıyla
3. Öncelikli konular tablosu, ardından net gidişatı grafiği + tahmin noktası

**Anlatım:**
> "Ustalık haritası: kırmızı konular zayıf, yeşiller güçlü — ve her birinin güven aralığı var,
> yani az veriyle kesin konuşmuyoruz. Aşağıda net gidişatı ve bir sonraki deneme kestirimi."

#### 1:50 – 2:10 — Haftalık Plan + Koç (kalıcı hafıza)

**Akış:**
1. Haftalık Plan sayfası → plan tablosu
2. Koç Sohbeti → "Nerelerde zayıfım?" → veriye dayalı cevap
3. **Sayfa yenilenir** → "Dün hangi konuya çalışmıştık?" → koç önceki konuşmayı hatırlıyor

**Anlatım:**
> "Sınav tarihim ve zaman bütçem tanımlı; haftalık plan otomatik çıkıyor.
> Koç öğrenciyi verisiyle tanıyor — ve sayfayı yenilesem bile konuşmayı hatırlıyor,
> çünkü hafızası kalıcı."

---

### 2:10 – 2:45 | AI Kanıtları (AI Evidence)

**Ne gösterilir:** Ekranda gerçek rapor dosyaları (slayt değil)

1. **Etiketleme doğruluğu** → `docs/etiketleme-dogruluk-raporu.md`
   > "120 gerçek ÖSYM sorusundan oluşan elle etiketli sette ölçtük: %76.7'den başlayıp
   > hata analiziyle %83.3'e çıkardık."

2. **Kendi sınıflandırıcımız** → `docs/siniflandirici-karsilastirma.md`
   > "Kendi modelimizi de eğittik: aynı sette %58.3. Gemini'yi geçmedi ve bunu dürüstçe
   > raporladık — ama API anahtarı olmadan, milisaniyede, sıfır maliyetle çalışıyor;
   > uygulamanın anahtarsız demo modunu o taşıyor."

3. **Kalibrasyon** → `docs/kalibrasyon.md`
   > "Bayesçi ustalık modelini 1000 sentetik öğrenciyle kalibre ettik; dikkatsizlik
   > senaryosu dahil ortalama hata 0.10."

4. **Agent mimarisi** → `README.md` mimari diyagramı
   > "LangGraph süpervizör mimarisi: yönlendirme deterministik, eğitmen/analist/planlayıcı
   > uzmanları orkestre ediyor, hafıza SQLite'ta kalıcı."

> ⚠️ **Net tahmin modeli (A5) burada iddia edilmeyecek.** Panodaki tahmin, deneme
> geçmişinden hesaplanan kestirimdir; GradientBoosting modeli sentetik kohortta eğitilip
> raporlanmış bir çalışmadır ve gerçek ölçekte yeniden eğitilmeden ürüne bağlanmadı.
> Söylenecekse tam olarak böyle söylenmeli — "panodaki tahmini o model üretiyor"
> izlenimi verilmemeli.

---

### 2:45 – 3:00 | Ekip + Gelecek

**Ne gösterilir:** GitHub repo + takım tablosu  
**Anlatım:**
> "Takım 76 — Bahar, Görkem, Doğa ve Emir Arda.
> Repo: github.com/Baharcakir/bootcamp-2026
> Sonraki adım: gerçek öğrenci pilotu, müfredat genişlemesi (TYT Türkçe, Fen)
> ve öğretmenlerin sınıflarını takip edeceği panel."

**Kapanış:** Logo + "Çarpan — Önce değer, sonra veri."

---

## 🎬 Çekim Notları

| Sahne | Araç | Not |
|---|---|---|
| Telefon fotoğrafı | Fiziksel telefon | Gerçek kağıt soru + gerçek çekim — slayt değil |
| Karne fotoğrafı | Fiziksel telefon | Gerçek bir deneme karnesi (isim/TC görünmesin) |
| Ekran kaydı | OBS / QuickTime | **Canlı URL üzerinden** — yerel sunucu değil |
| Metrikler | Tarayıcı | Markdown dosyaları GitHub'da açık — terminal/IDE değil |
| Kapanış | Ekran | GitHub repo + takım tablosu |

## ⚠️ Çekim Öncesi Kontrol

- [ ] Canlı arayüz açılıyor: https://carpan-tyt-kocu.streamlit.app/
- [ ] Açılışta **Demo Öğrenci** seçili geliyor ve pano dolu görünüyor
- [ ] Canlı API ayakta: `/health` → `{"status":"ok"}`
- [ ] Soru sorma, quiz, plan ve koç canlıda bir kez denendi (Gemini yanıt veriyor)
- [ ] Karne fotoğrafı hazır ve kişisel bilgi içermiyor
- [ ] Ekran çözünürlüğü 1080p+, ses test edildi
- [ ] Yedek: ekran kaydı önceden alındı (canlı demo riskine karşı)
- [ ] Süre prova edildi: **3 dakika aşılmıyor**
- [ ] Video YouTube'a **liste dışı veya herkese açık** yüklendi (gizli olursa jüri açamaz)
