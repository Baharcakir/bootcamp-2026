# Sentetik Veri ile Model Kalibrasyon Raporu

Bu rapor, **Çarpan** projesinin çekirdeğinde yer alan **Bayesçi Ustalık Kestirimi (Beta-Binomial)** modelinin doğruluğunu kanıtlamak ve model parametrelerini test etmek amacıyla hazırlanmıştır.

## Metodoloji ve Simülasyon Tasarımı

Modeli kalibre etmek için gerçeğe en yakın davranış sergileyen sentetik bir öğrenci popülasyonu simüle edilmiştir:

* **Öğrenci Sayısı:** 1000 sanal öğrenci.
* **Konu Dağılımı:** Matematik altındaki 5 temel konu (Üslü Sayılar, Köklü Sayılar, Fonksiyonlar, Polinomlar, Çarpanlara Ayırma).
* **Zaman Dilimi:** Son 60 günü kapsayan haftalık periyotlarda toplam 8 deneme sınavı geçmişi.
* **Şans Faktörü:** 5 şıklı TYT sınav formatına uygun olarak şans başarısı oranı (guessing rate) $p = 0.20$ olarak simülasyona yansıtılmıştır.
* **Boş Bırakma Faktörü:** Öğrencinin bilmediği sorularda %15 oranında boş bırakma ihtimali simüle edilmiştir.
* **Dikkatsizlik (Slip) Faktörü:** Öğrencinin bildiği sorularda %10 oranında dikkatsizlik nedeniyle yanlış cevaplama ihtimali eklenmiştir. Slip'li senaryo, insan davranışına çok daha gerçekçi bir yaklaşım sunmaktadır.

---

## Kalibrasyon Sonuçları

Simülasyon sonucunda, modelin tahmin ettiği şans düzeltmeli gerçek bilgi düzeyi (`estimated knowledge`) ile öğrencilerin simülasyon başında tanımlanan gerçek bilgi seviyeleri (`true knowledge`) karşılaştırılmıştır.

Elde edilen hata metrikleri şu şekildedir:

| Metrik | Değer | Açıklama |
| :--- | :--- | :--- |
| **Öğrenci Sayısı** | 1000 | Test edilen toplam tekil profil |
| **Ortalama Mutlak Hata (MAE)** | 0.1021 | Model tahminleri ile gerçek seviyeler arasındaki ortalama sapma (%10.21, 0-1 ölçeğinde) |
| **Kök Ortalama Kare Hata (RMSE)** | 0.1258 | Büyük hataları daha çok cezalandıran hata payı ölçüsü (%12.58, 0-1 ölçeğinde) |

> **Not:** Simülasyona %10 dikkatsizlik (slip) parametresi eklendiğinde hata payı beklendiği üzere bir miktar artış göstermiştir (~0.075 → ~0.10). Modelimiz şans düzeltmesi (guessing rate) yaparken, dikkatsizlik (slip) için doğrudan bir düzeltme yapmamaktadır; bu sebeple hatadaki bu artış modelin teorik sınırları dahilinde beklenen bir davranıştır.

---

## Analiz ve Değerlendirme

* **Tahmin Hassasiyeti ve Sınırlar:** MAE 0.1021 — modelin ustalık kestirimi, gerçek değerden 0-1 ölçeğinde ortalama $\pm0.1021$ sapıyor. Slip parametresinin getirdiği insani gürültü sebebiyle hata beklendiği gibi artsa da, model öğrencinin genel durumunu stabil bir aralıkta takip edebilmektedir.
* **Parametre Geçerliliği:** Modelde kullanılan varsayılan parametreler (`HALF_LIFE_DAYS = 30.0`, `GUESS_RATE = 0.20`, `PRIOR_ALPHA/BETA = 1.0`) slip faktörünün yarattığı dalgalanmaya rağmen sistemin stabil çalışmasını sağlamaktadır.
* **Sonuç:** Modelimiz, gerçekçi slip gürültüsü altındaki limitleri ve şans düzeltme başarısıyla şeffaf bir şekilde jüri karşısında savunulmaya hazırdır.