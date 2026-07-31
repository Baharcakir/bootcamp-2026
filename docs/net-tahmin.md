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

---

## 3. Ürüne Bağlanma Durumu ve Sınırlar

Model şu an **canlı üründe kullanılmamaktadır**; sentetik kohort üzerinde eğitilmiş ve
değerlendirilmiş bir araştırma çıktısıdır. Nedeni ölçek uyumsuzluğudur:

- Eğitimdeki `son_deneme_neti`, sentetik üretecin 5 konuluk alt kümesinden hesaplanır
  (aralık ≈ 0–21, ortalama 10.25). Gerçek TYT Matematik neti 0–40 aralığındadır; model
  gerçek netlerle beslendiğinde ürettiği sayı bu ölçekte anlam taşımaz.
- `sinyal_yogunlugu` özelliği sentetik üretimde rastgele atanmıştır; hedefle korelasyonu
  0.02'dir (fiilen gürültü). Modelin öğrendiği asıl sinyal `ustalik_ortalamasi`
  değişkenidir (korelasyon 0.68).

Arayüzdeki "bir sonraki deneme" tahmini, öğrencinin gerçek deneme geçmişinden hesaplanan
eğim kestirimidir (`GET /students/{id}/trend`) — bu model değildir.

**Sonraki adım:** sentetik üreteci gerçek TYT ölçeğine (0–40 net) taşıyıp modeli yeniden
eğitmek ve `ustalik_ortalamasi` + gerçek net + gerçek sinyal yoğunluğu ile besleyerek
ürüne bağlamak. Bu değişiklik kalibrasyon raporunun sayılarını da etkileyeceğinden
bootcamp teslimi sonrasına bırakılmıştır.