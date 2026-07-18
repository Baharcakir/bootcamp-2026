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
- Etiket dosyası: `data/osym/etiketleme.csv` — sütunlar: `kitapcik, soru_no, konu, nihai_konu, not`

## Kurallar

1. `konu` sütununu doldur; `nihai_konu` denetimden sonra kesinleşir, şimdilik boş kalır.
2. **Konu adını listeden aynen yazın** (aşağıda; kopyala-yapıştır en güvenlisi).
3. **Kararsız kaldığın soruda** en yakın konuyu seç ve `not` sütununa kısa bir işaret bırak
   (örn. "Denklem Çözme de olabilir") — işaretli sorular denetim listesini oluşturur.
4. Bir soru iki konuya da uyuyorsa çözümün *ağırlıklı* adımı hangi konudansa onu seç, nota belirt.
5. **Kapsam:** CSV yalnızca 2024-2026 kitapçıklarını içerir (120 soru → değerlendirme seti).
   40 soru (tek kitapçık) bile ilk doğruluk ölçümü için yeterli bir başlangıçtır; her ek
   kitapçık raporu güçlendirir. Eski yıllar (2018-2023) elle etiketlenmez — T6 eğitim verisi
   için gerektiğinde script'le eklenir ve yarı otomatik (öneri + onay) etiketlenir.
6. **Uyuşmazlık denetimi:** Otomatik ölçüm koşulduktan sonra, sistemin etiketiyle uyuşmayan
   sorular + `not` işaretli sorular ikinci kez incelenir (istersen bir ekip arkadaşıyla,
   ~15 dk) ve `nihai_konu` o zaman kesinleşir.
7. Tahmini süre: kitapçık başına ~30-45 dk.

## Konu Listesi (TYT Matematik — 27 konu, TTKB 2026 YKS belgesiyle doğrulandı)

Temel Kavramlar · Sayı Basamakları · Bölme ve Bölünebilme · EBOB-EKOK · Rasyonel Sayılar ·
Basit Eşitsizlikler · Mutlak Değer · Üslü Sayılar · Köklü Sayılar · Çarpanlara Ayırma ·
Oran-Orantı · Denklem Çözme · Problemler · Kümeler · Mantık · Fonksiyonlar · Polinomlar ·
İkinci Dereceden Denklemler · Permütasyon-Kombinasyon · Olasılık · Veri ve İstatistik ·
Doğruda ve Üçgende Açılar · Üçgenin Yardımcı Elemanları · Dik Üçgen ve Trigonometri ·
Üçgende Alan ve Benzerlik · Çokgenler ve Dörtgenler · Katı Cisimler

Not: Analitik Geometri ve Çember 11. sınıf konusudur, 2026 TYT kapsamı dışındadır — kitapçıkta
böyle bir soruya rastlarsan `not` sütununa yaz, birlikte karar veririz. Üçgen eşitsizliği ve
açı-kenar ilişkileri "Doğruda ve Üçgende Açılar" başlığına dahildir (MEB 9.4.1). Sınır
durumlarında doğruluk raporundaki tutarlılık kuralları uygulanır.

## Telif Notu

ÖSYM soruları kamuya açık yayımlanır; biz yine de soru içeriğini repoya koymuyoruz — repoda
yalnızca yıl + soru numarası + konu etiketi bulunur. PDF/görüntüler herkesin yerelinde kalır.
