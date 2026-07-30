import os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import joblib

# 1. Veriyi Oku
data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic_students.csv"))
df = pd.read_csv(data_path)

# 2. Features (Girdi) ve Target (Hedef) Ayrımı
X = df[['son_deneme_neti', 'ustalik_ortalamasi', 'sinyal_yogunlugu']]
y = df['sonraki_deneme_neti']

# Train / Test Ayrımı (%80 Eğitim, %20 Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Eğitimi (GradientBoosting)
model = GradientBoostingRegressor(random_state=42)
model.fit(X_train, y_train)

# 4. Tahmin ve Metrik Hesaplama
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# Baseline (Son denemenin aynısını tahmin etme varsayımı)
baseline_pred = X_test['son_deneme_neti']
baseline_mae = mean_absolute_error(y_test, baseline_pred)

print("\n" + "="*45)
print("MODEL EĞİTİMİ VE MAE RAPORU")
print("="*45)
print(f"Model MAE      : {mae:.4f}")
print(f"Model RMSE     : {rmse:.4f}")
print(f"Baseline MAE   : {baseline_mae:.4f}")
print("="*45)

# 5. Modeli Kaydetme
models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
os.makedirs(models_dir, exist_ok=True)
model_path = os.path.join(models_dir, "net_predictor.joblib")
joblib.dump(model, model_path)

print(f"\n✅ Model başarıyla kaydedildi: {model_path}")