import os
import sys
import random
from datetime import date, timedelta
import numpy as np

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
NUM_STUDENTS = 1000
SLIP_RATE = 0.10  # %10 Dikkatsizlik (Slip) ihtimali

def generate_student_data():
    """
    1000 tane sentetik öğrenci üretir. 
    Her öğrenci için 'gerçek' bir ustalık (true knowledge) seviyesi belirler.
    Ardından bu öğrencilere zamana yayılmış denemeler çözdürür ve modelin tahmin başarısını ölçer.
    """
    print(f"{NUM_STUDENTS} adet sentetik öğrenci için simülasyon başlatılıyor...")
    
    absolute_errors = []  # Modelin gerçek bilgi ile tahmin arasındaki farkları tutacağız (MAE için)
    
    for student_id in range(NUM_STUDENTS):
        # Her öğrenci için bu konularda rastgele bir Gerçek Bilgi Seviyesi belirliyoruz [0.0 - 1.0]
        true_knowledges = {topic: random.uniform(0.1, 0.9) for topic in TOPICS}
        
        student_observations = []
        today = date.today()
        
        # Öğrencinin son 60 günde her hafta 1 denemeye girdiğini simüle edelim (Toplam 8 deneme)
        for week in range(8):
            exam_date = today - timedelta(days=(7 * (7 - week))) # Eskiden yeniye doğru tarihler
            
            for topic in TOPICS:
                true_k = true_knowledges[topic]
                
                # Öğrencinin bu denemede o konudan kaç soruyla karşılaştığını belirliyoruz (Rastgele 3-6 soru)
                num_questions = random.randint(3, 6)
                correct = 0
                wrong = 0
                blank = 0
                
                # Her bir soru için öğrencinin doğru yapıp yapamayacağını simüle ediyoruz
                for _ in range(num_questions):
                    # Karar mekanizması: 
                    # Öğrenci konuyu biliyorsa (true_k olasılıkla) doğru çözer...
                    if random.random() < true_k:
                        # ...ama %10 ihtimalle dikkatsizlik (slip) yapıp yanlış cevap verir!
                        if random.random() < SLIP_RATE:
                            wrong += 1
                        else:
                            correct += 1
                    else:
                        # Bilmediği soruda %15 ihtimalle boş bıraksın, kalanı yanlış yapsın (şans başarısı hariç)
                        tahmin_olasiligi = random.random()
                        if tahmin_olasiligi < GUESS_RATE: # %20 Şans başarısı (Soru 5 şıklı)
                            correct += 1
                        elif tahmin_olasiligi < (GUESS_RATE + 0.15): # %15 Boş bırakma ihtimali (0.20 + 0.15 = 0.35)
                            blank += 1
                        else:
                            wrong += 1
                
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
        
        # --- 2. MODELİ TEST ETME ---
        # Bu öğrencinin tüm geçmiş deneme verilerini mastery.py'deki 'estimate_mastery' fonksiyonuna veriyoruz
        estimated_masteries = estimate_mastery(student_observations, today=today)
        
        for est in estimated_masteries:
            true_k = true_knowledges[est.topic]
            # Modelin tahmin ettiği şans düzeltmeli "gerçek bilgi" kestirimi ile bizim belirlediğimiz true_k arasındaki fark
            error = abs(est.knowledge - true_k)
            absolute_errors.append(error)

    # --- 3. RAPORLAMA ---
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

if __name__ == "__main__":
    generate_student_data()