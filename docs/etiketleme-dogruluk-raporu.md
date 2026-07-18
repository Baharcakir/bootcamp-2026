# T4 — Otomatik Konu Etiketleme Doğruluk Raporu

Çarpan'ın çekirdek özelliği olan otomatik konu etiketlemenin (soru görüntüsü → 27 konuluk TYT
Matematik taksonomisi) doğruluğu, gerçek ÖSYM sorularından oluşan bir değerlendirme setinde
ölçülmüştür.

## Yöntem

1. **Değerlendirme seti:** 2024, 2025 ve 2026 ÖSYM TYT kitapçıklarının Temel Matematik
   bölümlerindeki 120 soru (40'ar soru). Sorular repoya konmaz (telif); yıl + soru numarası +
   etiket paylaşılır (`data/osym/etiketleme.csv`).
2. **İnsan etiketleri:** Tek etiketçi + kararsızlık işaretleme yöntemi. 120 sorunun tamamı elle
   etiketlendi; 43 soruda "alternatif konu da olabilir" notu düşüldü (bkz. etiketleme yönergesi).
3. **Otomatik etiketleme:** gemini-2.5-flash modeline kitapçık sayfa görüntüleri verildi
   (sıcaklık 0, 37 çağrı); model her sayfadaki soruları taksonomiden etiketledi. 120/120 soru
   için etiket üretildi.
4. **Uyuşmazlık denetimi:** İlk ölçümdeki 28 uyuşmazlığın her biri soru görüntüsü üzerinden
   tek tek çözülerek incelendi ve "çözümün kilit tekniği hangi konudansa o" kuralıyla nihai
   etiket kararlaştırıldı. Kararların dağılımı: 20 insan etiketi, 5 model etiketi, 3 üçüncü konu.

## Sonuçlar

| Metrik | Değer |
|---|---|
| İlk ölçüm (insan etiketlerine karşı) | 92/120 = **%76.7** |
| **Nihai (denetim sonrası etiketlere karşı)** | 97/120 = **%80.8** |

| Kitapçık | Nihai doğruluk |
|---|---|
| 2024 | 30/40 (%75.0) |
| 2025 | 33/40 (%82.5) |
| 2026 | 34/40 (%85.0) |

Uyuşmazlıkların 23/28'inin, etiketçinin baştan "kararsızım" diye işaretlediği sorularda çıkması,
hataların rastgele değil **konu sınırlarının gerçekten bulanık olduğu sorularda** yoğunlaştığını
gösteriyor — 11 uyuşmazlıkta model, etiketçinin notuna yazdığı alternatifi seçmişti.

## Denetimde benimsenen tutarlılık kuralları

Sınır durumlarında etiket kararını standartlaştırmak için şu kurallar benimsendi (gelecek
etiketleme turlarında ve v2 prompt'ta kullanılacak):

1. **Grafik-merkezli soru → Veri ve İstatistik** (dairesel/sütun grafik okumak çözümün
   omurgasıysa).
2. **Pisagor'un kilit teknik olduğu soru → Dik Üçgen ve Trigonometri** (alan/çevre sadece
   çerçeveyse bile).
3. **Gerçek hayat senaryosunu modellemek işin ağırlığıysa → Problemler** (denklem kurma dahil).
4. **Yeni-tanımlı sayı soruları → tanımın işlediği konu** (asallık analizi → Temel Kavramlar,
   periyodik desen → Bölme ve Bölünebilme; MEB 9.3.2 periyodik problemleri açıkça Bölünebilme'ye
   koyar).
5. Üçgen eşitsizliği ve açı-kenar ilişkileri → "Doğruda ve Üçgende Açılar" (MEB 9.4.1 ile hizalı).

## Modelin sistematik hataları (iyileştirme hedefleri)

1. **"Problemler" çekim etkisi:** Kalan 23 hatanın 14'ünde model "Problemler" dedi. Yeni nesil
   TYT soruları hikâye bağlamına gömülü olduğundan model, çözüm tekniği yerine bağlama bakarak
   etiketliyor.
2. **3D görsel tuzağı:** Merdiven çizimli bir denklem sorusuna "Katı Cisimler" dedi (2024 s.18) —
   görselde üç boyutlu nesne görmek başlığı tetikliyor.
3. **"Mantık yürütme" karışması:** Sıralama-akıl yürütme sorusuna "Mantık" dedi (2024 s.26);
   taksonomideki Mantık başlığı önermeler konusudur.

**v2 planı:** Etiketleme prompt'una "konuyu bağlam hikâyesi değil, çözümün kilit tekniği belirler"
ilkesi + yukarıdaki tutarlılık kuralları eklenip ölçüm tekrarlanacak; T6'da kendi eğittiğimiz
sınıflandırıcı aynı sette karşılaştırılacak.

## Denetim izi

- Etiketler: `data/osym/etiketleme.csv` (konu = ilk elle etiket, nihai_konu = denetim sonrası)
- Uyuşmazlık kararları: `data/osym/uyusmazliklar.csv` (insan/model/nihai + etiketçi notu)
- Ölçüm script'i: `backend/scripts/measure_labeling.py` (yeniden koşturulabilir)
