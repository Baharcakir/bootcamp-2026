import os
import sys
import random
from datetime import date, timedelta
import numpy as np
import pandas as pd  # CSV kaydı için pandas eklendi

# Projenin root (kök) dizinini Python yoluna ekliyoruz ki mastery.py dosyasını import edebilelim
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.mastery import (
    estimate_mastery,
    TopicObservation,
    GUESS_RATE
)

# 1. PARAMETRELER VE KONULAR
SUBJECT = "Matematik"
TOPICS = ["Üslü Sayılar", "Köklü Sayılar", "Fonksiyonlar", "Polinomlar", "Çarpanlara Ayırma"]

# Rastgelelik sonuçlarının herkes için aynı çıkması amacıyla seed ekledik
random.seed(42)
np.random.seed(42)

NUM_STUDENTS = 1000
SLIP_RATE = 0.10  # %10 Dikkatsizlik (Slip) ihtimali

def generate_student_data():
    """
    1000 tane sentetik öğrenci üretir. 
    Her öğrenci için 'gerçek' bir ustalık (true knowledge) seviyesi belirler.
    Ardından bu öğrencilere zamana yayılmış denemeler çözdürür ve verileri data/synthetic_students.csv dosyasına kaydeder.
    """
    print(f"{NUM_STUDENTS} adet sentetik öğrenci için simülasyon başlatılıyor...")
    
    absolute_errors = []  # Modelin gerçek bilgi ile tahmin arasındaki farkları tutacağız (MAE için)
    dataset_rows = []     # CSV'ye yazılacak öğrenci verilerini burada toplayacağız
    
    for student_id in range(NUM_STUDENTS):
        # Her öğrenci için bu konularda rastgele bir Gerçek Bilgi Seviyesi belirliyoruz [0.0 - 1.0]
        true_knowledges = {topic: random.uniform(0.1, 0.9) for topic in TOPICS}
        
        student_observations = []
        today = date.today()
        
        # Öğrencinin deneme bazlı toplam netlerini tutmak için:
        exam_nets = []
        
        # Öğrencinin son 60 günde her hafta 1 denemeye girdiğini simüle edelim (Toplam 8 deneme)
        for week in range(8):
            exam_date = today - timedelta(days=(7 * (7 - week))) # Eskiden yeniye doğru tarihler
            
            total_correct = 0
            total_wrong = 0
            
            for topic in TOPICS:
                true_k = true_knowledges[topic]
                
                # Öğrencinin bu denemede o konudan kaç soruyla karşılaştığını belirliyoruz (Rastgele 3-6 soru)
                num_questions = random.randint(3, 6)
                correct = 0
                wrong = 0
                blank = 0
                
                # Her bir soru için öğrencinin doğru yapıp yapamayacağını simüle ediyoruz
                for _ in range(num_questions):
                    if random.random() < true_k:
                        if random.random() < SLIP_RATE:
                            wrong += 1
                        else:
                            correct += 1
                    else:
                        tahmin_olasiligi = random.random()
                        if tahmin_olasiligi < GUESS_RATE: # %20 Şans başarısı
                            correct += 1
                        elif tahmin_olasiligi < (GUESS_RATE + 0.15): # %15 Boş bırakma ihtimali
                            blank += 1
                        else:
                            wrong += 1
                
                total_correct += correct
                total_wrong += wrong
                
                # Gözlemi kaydediyoruz
                student_observations.append(
                    TopicObservation(
                        subject=SUBJECT,
                        topic=topic,
                        exam_date=exam_date,
                        correct=correct,
                        wrong=wrong,
                        blank=blank
                    )
                )
            
            # Bu haftaki denemenin toplam netini hesapla (Doğru - Yanlış / 4)
            week_net = total_correct - (total_wrong / 4.0)
            exam_nets.append(week_net)
        
        # --- 2. MODELİ TEST ETME ---
        estimated_masteries = estimate_mastery(student_observations, today=today)
        
        for est in estimated_masteries:
            true_k = true_knowledges[est.topic]
            error = abs(est.knowledge - true_k)
            absolute_errors.append(error)

        # --- CSV İÇİN SATIR OLUŞTURMA ---
        # Ustalık ortalaması
        avg_mastery = np.mean([est.knowledge for est in estimated_masteries])
        
        # Özellik Seti:
        # son_deneme_neti: 7. denemedeki net
        # sonraki_deneme_neti (Target): 8. denemedeki net
        dataset_rows.append({
            "student_id": student_id,
            "son_deneme_neti": round(exam_nets[-2], 2),       # Son yapılan deneme
            "ustalik_ortalamasi": round(avg_mastery, 4),      # Konu ustalık ortalaması
            "sinyal_yogunlugu": round(random.uniform(0.4, 1.0), 2), # Sinyal yoğunluğu
            "sonraki_deneme_neti": round(exam_nets[-1], 2)   # Tahmin edilecek sonraki deneme neti
        })

    # --- 3. CSV DOSYASINI SAVE ETME (data/synthetic_students.csv) ---
    df = pd.DataFrame(dataset_rows)
    
    # Proje ana dizinindeki 'data' klasörünün yolunu bulalım
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    
    csv_file_path = os.path.join(data_dir, "synthetic_students.csv")
    df.to_csv(csv_file_path, index=False)

    # --- 4. RAPORLAMA ---
    mae = np.mean(absolute_errors)
    rmse = np.sqrt(np.mean(np.square(absolute_errors)))
    
    print("\n" + "="*40)
    print("SENTETİK VERİ KALİBRASYON RAPORU ÖZETİ")
    print("="*40)
    print(f"Toplam Simüle Edilen Öğrenci: {NUM_STUDENTS}")
    print("Konu Başına Toplam Deneme Sayısı: 8 deneme/öğrenci")
    print(f"Ortalama Mutlak Hata (MAE): {mae:.4f}")
    print(f"Kök Ortalama Kare Hata (RMSE): {rmse:.4f}")
    print("="*40)
    print("Yorum: Slip (dikkatsizlik) senaryosu dahil edilmiştir. Modelin ustalık kestirim hatası gerçekçi insan davranışı altında test edilmiştir.")
    print(f"\n✅ Sentetik öğrenci verileri kaydedildi: {csv_file_path}")

if __name__ == "__main__":
    generate_student_data()