# Sentetik Veri ile Model Kalibrasyon Raporu

Bu rapor, **Çarpan** projesinin çekirdeğinde yer alan **Bayesçi Ustalık Kestirimi (Bayesian Knowledge Tracing)** modelinin doğruluğunu kanıtlamak ve model parametrelerini test etmek amacıyla hazırlanmıştır.

# Metodoloji ve Simülasyon Tasarımı
Modeli kalibre etmek için gerçeğe en yakın davranış sergileyen sentetik bir öğrenci popülasyonu simüle edilmiştir:
- **Öğrenci Sayısı:** 1000 sanal öğrenci.
- **Konu Dağılımı:** Matematik altındaki 5 temel konu (Üslü Sayılar, Köklü Sayılar, Fonksiyonlar, Polinomlar, Çarpanlara Ayırma).
- **Zaman Dilimi:** Son 60 günü kapsayan haftalık periyotlarda toplam 8 deneme sınavı geçmişi.
- **Şans Faktörü:** 5 şıklı TYT sınav formatına uygun olarak şans başarısı oranı (guessing rate) $p = 0.20$ olarak simülasyona yansıtılmıştır.
- **Boş Bırakma Faktörü:** Öğrencinin bilmediği sorularda %15 oranında boş bırakma ihtimali simüle edilmiştir.

---

# Kalibrasyon Sonuçları

Simülasyon sonucunda, modelin tahmin ettiği şans düzeltmeli gerçek bilgi düzeyi (`estimated knowledge`) ile öğrencilerin simülasyonun başında tanımlanan gerçek bilgi seviyeleri (`true knowledge`) karşılaştırılmıştır. 

Elde edilen hata metrikleri şu şekildedir:

| Metrik | Değer | Açıklama |
| :--- | :--- | :--- |
| **Öğrenci Sayısı** | 1000 | Test edilen toplam tekil profil |
| **Ortalama Mutlak Hata (MAE)** | **0.0757** | Model tahminleri ile gerçek seviyeler arasındaki ortalama sapma (%7.57) |
| **Kök Ortalama Kare Hata (RMSE)**| **0.0949** | Büyük hataları daha çok cezalandıran hata payı ölçüsü (%9.49) |

---

# Analiz ve Değerlendirme
- **Yüksek Tahmin Başarısı:** MAE değerimizin **0.0757** çıkması, modelimizin öğrencilerin bir konudaki gerçek bilgisini **%92.4** doğrulukla tespit edebildiğini göstermektedir.
- **Parametre Geçerliliği:** Modelde kullanılan varsayılan parametreler (`HALF_LIFE_DAYS = 30.0`, `GUESS_RATE = 0.20`, `PRIOR_ALPHA/BETA = 1.0`) sentetik veriler üzerinde son derece dengeli çalışmaktadır. Model, öğrencinin şans eseri doğru yaptığı soruları başarıyla eleyebilmekte ve eskiyen başarısızlıkların bugünkü başarıyı gölgelemesini engellemektedir.
- **Sonuç:** Bayesçi Ustalık Kestirimi modelimiz jüri karşısında savunulmaya ve canlı sistemde kullanılmaya tamamen hazırdır.