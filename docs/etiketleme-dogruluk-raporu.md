# T4 — Otomatik Konu Etiketleme Doğruluk Raporu (ilk ölçüm)

**Yöntem:** Değerlendirme seti, 2024-2026 ÖSYM TYT kitapçıklarının 120 matematik sorusudur.
Etiketler tek etiketçi + kararsızlık işaretleme yöntemiyle elle atandı (43 soru işaretli).
Otomatik etiketleme: gemini-2.5-flash modeline sayfa görüntüleri verildi (sıcaklık 0,
37 çağrı); model, sayfadaki soruları 27 konuluk taksonomiden etiketledi.
Bu ilk ölçümdür — uyuşmazlık denetimi (aşağıdaki liste + işaretli sorular) sonrası
nihai etiketlerle rapor güncellenecektir.

## Sonuçlar

| Metrik | Değer |
|---|---|
| Karşılaştırılan soru | 120/120 |
| Model etiketi eksik | 0 |
| **Doğruluk (ilk ölçüm)** | **92/120 = %76.7** |

| Kitapçık | Doğruluk |
|---|---|
| 2024 | 29/40 (%72.5) |
| 2025 | 30/40 (%75.0) |
| 2026 | 33/40 (%82.5) |

## Uyuşmazlıklar (28 soru — denetim turu listesi)

| Kitapçık | Soru | İnsan | Model | İnsan notu |
|---|---|---|---|---|
| 2024 | 3 | Üslü Sayılar | Problemler | Problemler de olabilir; ağırlıklı adım mandal sayısının üste |
| 2024 | 6 | Mutlak Değer | Problemler | Problemler de olabilir; ağırlıklı adım tahmin ile gerçek değ |
| 2024 | 7 | Temel Kavramlar | Problemler |  |
| 2024 | 9 | Rasyonel Sayılar | Temel Kavramlar | Oran-Orantı da olabilir; ağırlıklı adım eşit aralıklı sayı d |
| 2024 | 14 | Bölme ve Bölünebilme | Sayı Basamakları |  |
| 2024 | 18 | Oran-Orantı | Katı Cisimler | Problemler de olabilir; ağırlıklı adım basamak yükseklikleri |
| 2024 | 21 | Kümeler | Problemler | Problemler de olabilir; ağırlıklı adım doğru cevap kümelerin |
| 2024 | 26 | Problemler | Mantık | Permütasyon-Kombinasyon da olabilir; ağırlıklı adım iki sıra |
| 2024 | 27 | EBOB-EKOK | Problemler | Oran-Orantı da olabilir; ağırlıklı adım özdeş dikdörtgen fay |
| 2024 | 28 | Temel Kavramlar | Problemler | Bölme ve Bölünebilme de olabilir; ağırlıklı adım çarpan çift |
| 2024 | 35 | Üçgende Alan ve Benzerlik | Dik Üçgen ve Trigonometri | Dik Üçgen ve Trigonometri de olabilir; ağırlıklı adım benzer |
| 2025 | 1 | Rasyonel Sayılar | Problemler | Oran-Orantı da olabilir; ağırlıklı adım dolu bölme sayısının |
| 2025 | 4 | Rasyonel Sayılar | Sayı Basamakları | Sayı Basamakları da olabilir; ağırlıklı adım kesrin ondalık  |
| 2025 | 5 | İkinci Dereceden Denklemler | Problemler | Denklem Çözme de olabilir; tanımlı işlem sonucunda ikinci de |
| 2025 | 12 | Temel Kavramlar | Problemler | Sayı Basamakları da olabilir; ağırlıklı adım asal sayı koşul |
| 2025 | 15 | Sayı Basamakları | Problemler |  |
| 2025 | 16 | Kümeler | Veri ve İstatistik | Veri ve İstatistik de olabilir; ağırlıklı adım küme eleman s |
| 2025 | 18 | Rasyonel Sayılar | Problemler | Problemler de olabilir; ağırlıklı adım kümülatif isabet oran |
| 2025 | 23 | Veri ve İstatistik | Problemler |  |
| 2025 | 24 | Basit Eşitsizlikler | Problemler | Problemler de olabilir; ağırlıklı adım iki zaman aralığının  |
| 2025 | 36 | Dik Üçgen ve Trigonometri | Çokgenler ve Dörtgenler | Üçgende Alan ve Benzerlik de olabilir; ağırlıklı adım dik üç |
| 2026 | 5 | Denklem Çözme | Problemler |  |
| 2026 | 6 | Bölme ve Bölünebilme | Temel Kavramlar | Problemler de olabilir; ağırlıklı adım tam sayı çarpan çiftl |
| 2026 | 14 | Çokgenler ve Dörtgenler | Problemler | Problemler de olabilir; ağırlıklı adım çokgenlerin kenar say |
| 2026 | 23 | Veri ve İstatistik | Problemler | Problemler de olabilir; ağırlıklı adım dairesel grafik okuma |
| 2026 | 26 | Bölme ve Bölünebilme | Problemler | Problemler de olabilir; ağırlıklı adım bölüm-kalan. |
| 2026 | 32 | Doğruda ve Üçgende Açılar | Problemler | Üçgen eşitsizliği; listede ayrı konu başlığı yok. |
| 2026 | 33 | Üçgende Alan ve Benzerlik | Problemler | Dik Üçgen ve Trigonometri de olabilir; ağırlıklı adım üçgen  |

## En sık karışan konu çiftleri (insan → model)

- Temel Kavramlar → Problemler: 3
- Rasyonel Sayılar → Problemler: 2
- Veri ve İstatistik → Problemler: 2
- Üslü Sayılar → Problemler: 1
- Mutlak Değer → Problemler: 1
- Rasyonel Sayılar → Temel Kavramlar: 1
- Bölme ve Bölünebilme → Sayı Basamakları: 1
- Oran-Orantı → Katı Cisimler: 1

## Notlar

- Polinomlar, Çarpanlara Ayırma ve Üçgenin Yardımcı Elemanları 2024-2026 setinde hiç
  görülmedi; bu konularda ölçüm yapılamadı.
- Sonraki adım: uyuşmazlık denetimi → `nihai_konu` doldurulur → rapor nihai sayılarla
  güncellenir; aynı set T6'da kendi sınıflandırıcımızla karşılaştırma için kullanılır.

*Denetim listesi: `data/osym/uyusmazliklar.csv` (28 satır)*
