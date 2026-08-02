# T6 — Kendi Konu Sınıflandırıcımız vs Gemini (karşılaştırma raporu)

**Soru:** Konu etiketlemeyi Gemini'ye (zero-shot) yaptırmak yerine kendi
eğittiğimiz bir model aynı işi ne kadar iyi yapar?

**Veri:** Eğitim = 2018-2023 ÖSYM soruları (Gemini transkripsiyonu + iki bağımsız
model görüşü; çelişkiler T4 tutarlılık kurallarıyla tek tek karara bağlandı ve her
etiket insan onayından geçti) ve bağımsız çözücü doğrulamasından geçmiş AI
üretimi sorular. Değerlendirme = T4'teki 120 soruluk, elle etiketli 2024-2026 seti;
eğitime hiçbir biçimde girmez (bu script kodla zorlar).

**Yöntem dürüstlüğü:** Hiperparametreler ve kol seçimi yalnız eğitim verisinde
çapraz doğrulamayla yapıldı; doğrulama katmanları her kolda yalnız gerçek ÖSYM
örnekleridir (AI soruları sadece eğitim katmanlarına girer — böylece kollar aynı
dağılımda, karşılaştırılabilir ölçülür). Değerlendirme setine model seçiminde
bakılmadı; kayıtlı model CV'ye göre en iyi koldur.

## Sonuçlar (aynı 120 soruda)

| Model / kol | Eğitim boyutu | CV (ÖSYM katmanları) | Eval doğruluk |
|---|---|---|---|
| Gemini 2.5 Flash zero-shot (v2 kurallı prompt) | — | — | **%83.3** |
| TF-IDF + LogReg — yalnız ÖSYM | 240 | %52.1 | %57.5 (69/120) |
| TF-IDF + LogReg — ÖSYM + tüm AI ★ | 557 | %57.1 | %58.3 (70/120) |
| TF-IDF + LogReg — ÖSYM + hedefli AI (az örnekli konulara) | 320 | %53.7 | %63.3 (76/120) |

★ Kayıtlı model (`backend/app/data/konu_siniflandirici.joblib`): **ÖSYM + tüm AI** — char_wb(2, 5), C=4.0, cw=balanced

## Bulgular

- **Gemini %83.3 vs bizim model %58.3.** 27 sınıflı problemde ~500 örnekle eğitilen klasik bir modelle milyarlarca
  parametreli bir modelin farkı dürüstçe raporlanmıştır; hedef Gemini'yi geçmek
  değil, farkı ve kendi modelimizin değer önerisini ölçmektir.
- **AI soruları eklemek doğruluğu artırdı** (ablasyon): az örnekli konuların kapsanması stil maliyetinden ağır bastı.
- **Küçük veri notu:** ~50 örneklik doğrulama katmanlarında ±4-5 puanlık
  gürültü doğaldır; CV ile eval sıralaması bu bant içinde yer değiştirebilir
  (tabloda üç kol da şeffaf verilmiştir, seçim kuralı eval'e bakmaz).
- **AI soruları üç modelle üretildi** (çoğunluk Gemini 2.5 Flash; son ~%20
  Gemini 3 Flash / Flash-Lite — model erişim değişikliği nedeniyle) ve tamamı
  bağımsız çözücü doğrulamasından geçti.
- **Üründe gerçek kullanım (demo modu):** GOOGLE_API_KEY yokken yazılı sorular bu
  modelle etiketlenir, sinyal düşer ve zayıflık haritası anahtarsız da işlemeye
  devam eder (`app/services/classifier.py` + `/ask` akışı, testli). Anahtar varken
  etiket, anlatımla birlikte Gemini'den gelir — model API'siz, ~milisaniyede,
  sıfır maliyetle çalışır.

## En çok hata yapılan konular (kayıtlı model)

| Konu | Hata |
|---|---|
| Problemler | 13 |
| Rasyonel Sayılar | 5 |
| Mutlak Değer | 4 |
| Bölme ve Bölünebilme | 4 |
| Veri ve İstatistik | 3 |
| Üçgende Alan ve Benzerlik | 3 |
| Kümeler | 3 |
| Üslü Sayılar | 2 |

## En sık karışan çiftler (gerçek → tahmin)

- Veri ve İstatistik → Problemler: 3
- Mutlak Değer → Basit Eşitsizlikler: 2
- Bölme ve Bölünebilme → Sayı Basamakları: 2
- Problemler → Kümeler: 2
- Permütasyon-Kombinasyon → Problemler: 2
- Problemler → Rasyonel Sayılar: 2
- Problemler → Çokgenler ve Dörtgenler: 2
- Rasyonel Sayılar → Bölme ve Bölünebilme: 1

*Üretim: `backend/scripts/train_classifier.py` (seed 42, CV tabanlı seçim,
deterministik). Eğitim verisi telif nedeniyle repoda değildir (data/osym/raw/).*
