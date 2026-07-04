# Çarpan — Ürün Tanımı

> Bu belge, akademinin istediği "Ürün Fikrini ve Rolleri Belgelemek" başlıklarını birebir karşılar;
> form doldururken buradan kopyalayabilirsiniz.

## Takım İsmi

[TAKIM İSMİ — doldurun]

## Takım Rolleri

| İsim | Rol | Sorumluluk odağı (öneri) |
|---|---|---|
| [AD] | Product Owner | Backlog önceliklendirme + veri bilimi (ustalık/tahmin modelleri, kalibrasyon) |
| [AD] | Scrum Master | Akademi iletişimi, sprint belgeleri + backend (API) |
| [AD] | Developer | Agent mimarisi (LangGraph, araçlar, hafıza, süpervizör) |
| [AD] | Developer | Eğitmen hattı (Gemini Vision, RAG, quiz üretimi, etiket kalitesi) |
| [AD] | Developer | Arayüz (Streamlit), deploy, demo videosu |

> Not: Rol dağılımı önerisidir; PDF'teki kurala göre PO ve SM dahil herkes geliştirme yapar.

## Ürün İsmi

**Çarpan** — "Netlerinin çarpanı."
(Matematikteki *çarpan* + öğrencinin başarısını katlayan *çarpan etkisi* — isim ürünün vaadinin kendisi.)

## Ürün Açıklaması

Çarpan, YKS'ye hazırlanan öğrencinin **çözemediği TYT Matematik sorusunu fotoğraflayıp anında
anlatım aldığı** ve bu kullanımdan **kendiliğinden kişisel zayıflık haritası + çalışma planı
üretilen** yapay zeka koçudur.

**Çekirdek döngü (ürünün farkı burada):**

1. Öğrenci takıldığı sorunun fotoğrafını atar (veya yazar).
2. Eğitmen yapay zeka soruyu adım adım anlatır — değer anında verilir.
3. Aynı anda soru, sistemin TYT taksonomisine göre **otomatik olarak konu etiketlenir** ve
   zayıflık sinyali olarak kaydedilir. **Öğrenci hiçbir zaman konu seçmez, veri girmez.**
4. Sinyaller biriktikçe Bayesçi ustalık haritası, konu öncelikleri ve haftalık plan
   kendiliğinden oluşur; hafızalı koç bunların üzerinden konuşur.
5. Denemelerden yalnızca ders bazında net girilir (4-5 satır, ~10 saniye) — net gidişatı ve
   tahmin bunu kullanır. İleride karne fotoğrafından otomatik okunur (T5).

**Problem:** Soru çözüm uygulamaları soruyu anlatır ama öğrenciyi tanımaz; koçluk hizmetleri
öğrenciyi tanır ama pahalıdır ve veriye değil sezgiye dayanır. "Analiz" vaat eden araçlar ise
öğrenciden ödev gibi veri girişi ister — kimse girmez, araç terk edilir.

**Çözüm:** Yardım istemek zaten doğal davranıştır. Çarpan analitiği bu doğal davranışın yan ürünü
yapar: her sorulan soru hem anında cevaplanır hem de öğrenci modelini besler. Önce değer, sonra veri.

## Kapsam (v1): Neden Sadece TYT Matematik?

Bilinçli bir giriş stratejisi — dağınık bir "her ders" ürünü yerine tek derste kusursuzluk:

1. **En acı nokta:** Matematik, adayların en çok korktuğu ve net varyansının en yüksek olduğu
   ders; koçluk talebinin merkezi.
2. **Ölçülebilir kalite:** Adım adım anlatım ve otomatik konu etiketleme matematikte nesnel
   olarak doğrulanabilir (T4 değerlendirme seti); paragraf/sosyal anlatımı öznel kalır.
3. **Analitik değer:** TYT Matematik 26 konuya yayılır — harita gerçekten bilgi taşır. (Türkçe'nin
   ~26/40'ı tek konudur: Paragraf; harita anlamsızlaşır.)
4. **Maliyet:** RAG korpusu, quiz doğrulama ve değerlendirme seti tek müfredatta 4 kat ucuz.

**Genişleme yolu:** Mimari ders-bağımsız (taksonomi + korpus dosyasıyla genişler):
TYT Matematik → AYT Matematik → Fen → tüm YKS. Deneme neti takibi bugün bile tüm dersleri kapsar.

## Platform Kararı: Neden Mobil-Öncelikli Web?

1. **Çekirdek akışın doğal cihazı telefon:** Öğrenci masasında çalışırken takıldığı sorunun
   fotoğrafını telefonuyla çeker. Mobil tarayıcıda dosya yükleme doğrudan kamerayı açar
   (arayüzde ayrıca kamera sekmesi var) — fotoğraf akışı için native uygulama gerekmez.
2. **Sıfır kurulum sürtünmesi:** Link tıklanır, ürün açılır. İlk kullanıcı edinimi için de,
   jürinin "tıkla ve dene" deneyimi için de en kısa yol. (Rubrik: canlıya alınmış ürün — 10 puan.)
3. **Tek codebase, iki ekran:** Aynı web uygulaması telefonda soru sorma, masaüstünde analiz
   panosu deneyimini karşılar; 5 kişilik ekibin gücü modele harcanır, platform çoğaltmaya değil.
4. **Yol haritası:** PWA ("ana ekrana ekle") ile mağazasız uygulama hissi ara adım; bildirimli
   native uygulama (plan hatırlatmaları, offline) v2'de — web ile doğrula, uygulamayla derinleş.

## Veri ve Model Stratejisi (özet)

- **ÖSYM çıkmış soruları:** etiketleme doğruluğunun ölçüldüğü değerlendirme seti (T4), RAG
  korpusu (T2) ve kendi konu sınıflandırıcımızın eğitim verisi (T6). Kamuya açık, kaynak
  belirtilerek kullanılır; yayınevi soruları kullanılmaz.
- **AI üretimi sorular:** doğrulama süzgecinden geçirilip quiz bankasına (T3) ve sınıflandırıcı
  eğitim setine (T6) girer.
- **Sentetik öğrenci kohortları:** ustalık modelinin kalibrasyonu (A4) ve net tahmin modelinin
  eğitimi (A5). Sentetik olduğu açıkça raporlanır.
- **LLM (Gemini) eğitilmez** — kendi modellerimiz eğitilir/kalibre edilir. Detay: [mimari.md](mimari.md)

## Ürün Özellikleri

- 📸 **Soru anlatımı (TYT Matematik):** fotoğraf/metin → adım adım çözüm (Gemini Vision), müfredat
  kaynaklı ve çıkmış soru referanslı (RAG, T2); kapsam dışı sorulara nazik yönlendirme
- 🏷️ **Otomatik konu etiketleme:** yapay zeka her soruyu 26 konuluk taksonomiye göre sınıflandırır;
  doğruluğu ÖSYM çıkmış sorularında ölçülür (T4), Sprint 3'te kendi eğittiğimiz sınıflandırıcıyla
  karşılaştırılır (T6)
- 🗺️ **Kendiliğinden oluşan zayıflık haritası:** güven aralıklı Bayesçi ustalık skorları; sorulan
  sorular, "takıldım" işaretleri ve quiz sonuçlarından beslenir
- 🔁 **Mini quiz:** anlatımdan sonra doğrulanmış benzer soruyla deneme; doğru cevap ustalığı
  yukarı günceller (T3)
- 🗓️ **Haftalık kişisel plan:** sınav tarihi, saat bütçesi ve konu önceliklerinden (B3)
- 📈 **Net gidişatı ve tahmin:** 10 saniyelik ders-bazlı deneme girişi (tüm dersler); eğitilmiş
  tahmin modeli (A5)
- 💬 **Hafızalı koç:** analiz araçlarını kendisi çağıran, geçmişi hatırlayan LangGraph agent'ı
- 📷 **Karne okuma (T5):** deneme netlerini karne fotoğrafından otomatik alma

## Hedef Kitle

- YKS adayları (11-12. sınıf + mezun). Pazar: yılda ~3 milyon başvuru.
- Özellikle dershaneye/özel koçluğa erişimi olmayan öğrenciler (maliyet avantajı).
- İkincil: öğretmenler ve butik kurslar — öğrenci kohortunu tek panelden izleme (B2B, v2).

## Değer Önerisi ve Gelir Modeli (pazar potansiyeli için)

- **Değer:** "Bu soruyu anlamadım" anının çözümü + "bugün ne çalışmalıyım" sorusuna veriye dayalı
  cevap, koçluk maliyetinin çok altında.
- **Gelir modeli (fikir):** Freemium — günlük N soru ücretsiz; sınırsız soru, quiz ve detaylı plan
  premium. B2B kurum paneli ayrı paket.
- **Rakiplerden farkı:** Soru çözüm uygulamaları (Kunduz vb.) *soruya* odaklanır ve orada durur;
  Çarpan her sorudan *öğrenci modeli* çıkarır — anlatım aynı zamanda teşhistir. Uzun vadeli değer
  (harita + plan + koç) üründe kalır.

## Veri ve Etik Notu

- Demo ve model geliştirme sentetik öğrenci verisiyle yapılır; gerçek kullanıcı verisi toplanırsa
  KVKK kapsamında açık rıza ve veli onayı (18 yaş altı) gerekir — ürün sayfasında belirtilecek.
- Koç, tıbbi/psikolojik destek gereken durumlarda profesyonel yardıma yönlendirir.

## Product Backlog

Product backlog sprint board'u üzerinde yönetilir: [link eklenecek]
