# Veri Kaynakları ve Toplama Rehberi

> Sorumlular: Kişi 4 (eğitmen/veri) + PO. Sprint 2 başında (6 Temmuz) hazır olmalı.
> Etiketleme ve eğitim/değerlendirme ayrımının demir kuralları: [mimari.md → Veri Protokolü](mimari.md)

## 1. ÖSYM Çıkmış TYT Matematik Soruları (gerçek veri — tek gerçek kaynak)

- **Nerede:** osym.gov.tr → "Çıkmış Sorular / Temel Soru Kitapçıkları" bölümü. TYT 2018'den beri
  her yıl yayımlanıyor (~40 matematik sorusu/yıl → toplam ~320 soru). Ayrıca ÖSYM'nin yayımladığı
  örnek soru kitapçıkları da eklenebilir.
- **Nasıl işlenir:** PDF'lerden soru bazında ayıklama (metin + varsa şekil görüntüsü);
  `data/osym/` altında soru başına kayıt (yıl, soru no, metin, görsel yolu).
- **Kullanım:** ~100 soru → değerlendirme seti (elle çift etiket, dokunulmaz);
  kalan ~220 → sınıflandırıcı eğitimi (T6) + RAG korpusu (T2).
- **Telif:** ÖSYM soruları kamuya açık yayımlanır; kaynak (yıl/sınav) belirtilir, repo içinde
  toplu ham yeniden yayım yapılmaz (işlenmiş/atıflı kullanım). **Yayınevi denemeleri telifli —
  kesinlikle kullanılmaz.**

## 2. MEB Kazanımları (RAG korpusunun omurgası)

- **Nerede:** mufredat.meb.gov.tr → Ortaöğretim Matematik Dersi (9-12) Öğretim Programı.
  Kazanım listeleri konu anlatımının "müfredat dili"ni ve eğitmenin kaynak göstermesini sağlar.
- **Kullanım (T2):** kazanımlar konu başına bölünüp Chroma'ya işlenir; eğitmen anlatırken
  ilgili kazanımı çeker ve kaynak gösterir.

## 3. AI Üretimi Sorular (sentetik veri — üretim protokolü zorunlu)

1. **Üretim:** Gemini'ye konu + zorluk + 2-3 gerçek çıkmış soru (stil çapası) verilir;
   soru + 5 şık + doğru cevap + adım adım çözüm istenir.
2. **Doğrulama:** aynı soru bağımsız ikinci bir LLM çağrısıyla çözdürülür; cevaplar
   uyuşmuyorsa soru elenir. Kalanlardan örneklem insan gözüyle denetlenir.
3. **Kullanım:** quiz bankası (T3) + T6 eğitim setinde az örnekli konuları dengeleme.
   **Değerlendirme setine asla girmez.**

## 4. Sentetik Öğrenci Kohortları (A3)

- Parametrik üreteç: "konu başına gerçek ustalık" profili çizilir → sinyaller ve deneme
  sonuçları bu profilden örneklenir (soru sorma sıklığı zayıflıkla artar, quiz başarısı
  ustalıkla artar, netler ustalık toplamından türer + gürültü).
- Kullanım: ustalık modeli kalibrasyonu (A4 — "model gerçek ustalığı yakalıyor mu?") ve
  net tahmin modeli eğitimi (A5). Raporlarda "sentetik" olduğu açıkça yazılır.

## Yapılacaklar (Sprint 2 girişi)

- [ ] ÖSYM PDF'leri indirildi ve soru bazında ayıklandı (kişi 4)
- [ ] 100 soruluk değerlendirme adayı seçildi; çift etiketleme turu planlandı (PO + kişi 4)
- [ ] MEB kazanım dokümanı indirildi, konu eşlemesi yapıldı (kişi 4)
- [ ] AI soru üretim + doğrulama script taslağı (kişi 4, T3 ile birlikte)
