# T4 Etiketleme Yönergesi — ÖSYM Değerlendirme Seti

**Amaç:** Otomatik konu etiketlemenin doğruluğunu gerçek ÖSYM sorularında ölçmek. Bunun için
iki kişi, aynı soruları **birbirinden bağımsız** olarak elle etiketler; sistemin etiketleri
bu "insan mutabakatıyla" karşılaştırılır.

## Dosyalar

- Soru görüntüleri: `data/osym/raw/<yıl>/mat-XX.png` (herkes kendi bilgisayarında üretir:
  kitapçık PDF'lerini `data/osym/raw/` altına koyup `python backend/scripts/prepare_osym_eval.py`
  çalıştırmak yeterli — PDF/PNG'ler repoya girmez, yalnızca bu CSV paylaşılır)
- Etiket dosyası: `data/osym/etiketleme.csv` — sütunlar: `kitapcik, soru_no, etiketci1_konu,
  etiketci2_konu, nihai_konu, not`

## Kurallar

1. **Bağımsızlık şart:** Etiketçi 1 (Görkem) yalnızca `etiketci1_konu`, Etiketçi 2 (Doğa)
   yalnızca `etiketci2_konu` sütununu doldurur. Doldururken birbirinizin sütununa BAKMAYIN —
   ölçümün güvenilirliği buna bağlı.
2. **Konu adını listeden aynen yazın** (aşağıda; kopyala-yapıştır en güvenlisi).
3. Kararsız kaldığında en yakın konuyu seç, `not` sütununa kısa gerekçe yaz.
4. Bir soru iki konuya da uyuyorsa çözümün *ağırlıklı* adımı hangi konudansa onu seç, nota belirt.
5. **Öncelik sırası:** önce 2026, 2025, 2024 kitapçıkları (120 soru → değerlendirme setimiz).
   Kalan yıllar sınıflandırıcı eğitimi (T6) ve RAG için sonra etiketlenir.
6. İkiniz de bitirince uyuşmazlıklar üçüncü bir ekip üyesiyle konuşulup `nihai_konu` doldurulur.
   Uyuşma oranı (inter-annotator agreement) doğruluk raporuna yazılır.
7. Tahmini süre: kitapçık başına ~30-45 dk.

## Konu Listesi (TYT Matematik — 26 konu)

Temel Kavramlar · Sayı Basamakları · Bölme ve Bölünebilme · EBOB-EKOK · Rasyonel Sayılar ·
Basit Eşitsizlikler · Mutlak Değer · Üslü Sayılar · Köklü Sayılar · Çarpanlara Ayırma ·
Oran-Orantı · Denklem Çözme · Problemler · Kümeler · Mantık · Fonksiyonlar ·
Permütasyon-Kombinasyon · Olasılık · Veri ve İstatistik · Doğruda ve Üçgende Açılar ·
Özel Üçgenler ve Dik Üçgen · Üçgende Alan ve Benzerlik · Çokgenler ve Dörtgenler ·
Çember ve Daire · Katı Cisimler · Analitik Geometri

## Telif Notu

ÖSYM soruları kamuya açık yayımlanır; biz yine de soru içeriğini repoya koymuyoruz — repoda
yalnızca yıl + soru numarası + konu etiketi bulunur. PDF/görüntüler herkesin yerelinde kalır.
