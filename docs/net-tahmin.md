# Net Tahmin Modeli Performans Raporu

## 1. Kullanılan Özellik Seti (Features) & Target
* **Model:** Scikit-learn GradientBoostingRegressor
* **Girdi Özellikleri (Features):**
  - `son_deneme_neti`: Öğrencinin bir önceki denemede yaptığı net
  - `ustalik_ortalamasi`: Öğrencinin konular bazındaki ustalık puan ortalaması
  - `sinyal_yogunlugu`: Öğrencinin soru çözme aktivite yoğunluğu
* **Hedef Değişken (Target):** `sonraki_deneme_neti`

---

## 2. Metrikler ve Performans Karşılaştırması

Model performansı 1000 sentetik öğrenci verisi üzerinden %80 Eğitim / %20 Test ayrımı ile değerlendirilmiştir.

| Metrik | GradientBoosting Modeli | Baseline (Son Deneme Neti) | Değişim / İyileşme |
| :--- | :---: | :---: | :---: |
| **MAE (Mean Absolute Error)** | **2.0981** | 3.1700 | **~%33.8 İyileşme** |
| **RMSE (Root Mean Squared Error)** | **2.6869** | - | - |

> **Özet Yorum:** GradientBoosting tabanlı net tahmin modelimiz, öğrencinin sadece son netine bakan temel çizgiye (baseline) kıyasla hata oranını yaklaşık %34 düşürmüştür. Model dosyası `backend/models/net_predictor.joblib` konumuna kaydedilmiştir.