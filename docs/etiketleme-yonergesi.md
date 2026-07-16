# T4 Etiketleme Yönergesi — ÖSYM Değerlendirme Seti

**Amaç:** Otomatik konu etiketlemenin doğruluğunu gerçek ÖSYM sorularında ölçmek.

**Yöntem:** Tek etiketçi + kararsızlık işaretleme + uyuşmazlık denetimi. Sorular elle
etiketlenir; otomatik ölçüm koşulduktan sonra sistemle uyuşmayan ve "kararsızım" diye
işaretlenmiş sorulara ikinci kez bakılarak nihai etiketler kesinleşir. Doğruluk raporuna
yöntem bu şekilde yazılır.

## Dosyalar

- Soru görüntüleri: `data/osym/raw/<yıl>/mat-XX.png` (herkes kendi bilgisayarında üretir:
  kitapçık PDF'lerini `data/osym/raw/` altına koyup `python backend/scripts/prepare_osym_eval.py`
  çalıştırmak yeterli — PDF/PNG'ler repoya girmez, yalnızca bu CSV paylaşılır)
- Etiket dosyası: `data/osym/etiketleme.csv` — sütunlar: `kitapcik, soru_no, etiketci1_konu,
  etiketci2_konu, nihai_konu, not`

## Kurallar

1. Etiketçi yalnızca `etiketci1_konu` sütununu doldurur. (`etiketci2_konu` boş kalır;
   ileride ikinci bir göz katılırsa kullanılır.)
2. **Konu adını listeden aynen yazın** (aşağıda; kopyala-yapıştır en güvenlisi).
3. **Kararsız kaldığın soruda** en yakın konuyu seç ve `not` sütununa kısa bir işaret bırak
   (örn. "Denklem Çözme de olabilir") — işaretli sorular denetim listesini oluşturur.
4. Bir soru iki konuya da uyuyorsa çözümün *ağırlıklı* adımı hangi konudansa onu seç, nota belirt.
5. **Öncelik sırası:** önce 2026, 2025, 2024 kitapçıkları (120 soru → değerlendirme setimiz).
   Kalan yıllar sınıflandırıcı eğitimi (T6) ve RAG için sonra etiketlenir.
6. **Uyuşmazlık denetimi:** Otomatik ölçüm koşulduktan sonra, sistemin etiketiyle uyuşmayan
   sorular + `not` işaretli sorular ikinci kez incelenir (istersen bir ekip arkadaşıyla,
   ~15 dk) ve `nihai_konu` o zaman kesinleşir.
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
