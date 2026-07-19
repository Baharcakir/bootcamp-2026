# Sprint 2 Raporu — 6-19 Temmuz 2026 · Takım 76 · Çarpan

## Sprint Notları

Sprint hedefi: çekirdek döngüyü kapatmak ve kaliteyi ölçmek — kaynaklı anlatım (T2), doğrulanmış
quiz (T3), etiketleme doğruluğunun gerçek ÖSYM sorularında ölçülmesi (T4), sentetik veri ve
kalibrasyon (A3-A4), süpervizör agent mimarisi (B2) ve haftalık plan (B3).

Sprint başında işler kişi başına "görev paketleri" olarak dağıtıldı (5 paket). Sprint ortasında
kod işbirliği dal + Pull Request + gözden geçirme düzenine geçirildi (PR #1, PR #2).

**Takım değişikliği:** Ece, sprint sonunda bootcamp'ten ayrıldı; takım 5 kişiden 4 kişiye düştü.
Üzerindeki süreç işleri (rapor, board, teslim seti) Görkem'e, arayüz işleri (C2, C3) Bahar'a
devredildi. Durum akademiye Scrum Master tarafından bildirildi.

## Tahmin Edilen ve Gerçekleşen Puan

Sprint 2 planı **64 puandı**; **56 puan tamamlandı**, 8 puanlık iki iş (C2, C3) sprint
kapanışına kadar Bahar tarafından tamamlanıyor.

| Story | Puan | Durum |
|---|---|---|
| T2 — Kaynaklı anlatım (MEB kazanımı + çıkmış soru önerisi) | 8 | ✅ |
| T3 — Doğrulanmış quiz + ustalık güncelleme döngüsü | 8 | ✅ |
| T4 — ÖSYM değerlendirme seti + doğruluk raporu | 5 | ✅ (v2 iyileştirmesiyle) |
| A3 — Sentetik öğrenci üreteci | 8 | ✅ |
| A4 — Ustalık modeli kalibrasyonu (MAE 0.076) | 8 | ✅ |
| B2 — Süpervizör agent mimarisi (testli yönlendirme) | 5 | ✅ |
| B3 — Haftalık plan (deterministik servis + DB + arayüz) | 8 | ✅ |
| D3 — Test kapsamı (12 → 30 test) | 4 | ✅ |
| E2 — Sprint 2 teslim seti | 2 | ✅ (bu klasör) |
| C2 — Soru sorma mobil UX turu | 3 | 🔄 Bahar'da — sprint kapanışına kadar |
| C3 — Pano cilası (matematik neti ayrı seri) | 5 | 🔄 Bahar'da — sprint kapanışına kadar |

**Not:** C2/C3, ayrılan üyenin işleriydi; sprint sonunda Bahar'a devredildi. Kapanışa
yetişmezse Sprint 3 planına ilk sıradan alınacak ve bu rapor güncellenecektir.

## Öne Çıkan Çıktı: Ölç → İyileştir → Doğrula Döngüsü

Otomatik konu etiketleme, 120 gerçek ÖSYM sorusundan oluşan elle etiketli sette ölçüldü:

| Aşama | Doğruluk |
|---|---|
| İlk ölçüm | %76.7 |
| Uyuşmazlık denetimi sonrası (nihai etiketler) | %80.8 |
| Kural-iyileştirmeli v2 prompt | **%83.3** |

Detay: [docs/etiketleme-dogruluk-raporu.md](../../docs/etiketleme-dogruluk-raporu.md)
(yöntem, sistematik hata analizi, tutarlılık kuralları, denetim izleri).

## Daily Scrum

Bu sprintte daily ritmi düzenli işlemedi; koordinasyon büyük ölçüde PR açıklamaları ve birebir
mesajlaşma üzerinden yürüdü. Bunu retrospektifte iyileştirme maddesi olarak ele aldık
(aşağıda). Not formatı [DailyScrum/README.md](DailyScrum/README.md) dosyasındadır; Sprint 3'te
her akşam kısa yazılı daily'ye dönülecektir.

## Sprint Board

Board, Sprint 1'de kurulan Miro panosunda yürütülmektedir (kırmızı = task, mavi = story).
Sprint 2 sonu board görüntüleri: `screenshots/board-sprint2-*.png`

## Ürün Durumu

Ekran görüntüleri [screenshots/](screenshots/) klasöründe:

1. `urun-1-soru-sor.png` — fotoğraf/metin → anlatım + otomatik konu etiketi + MEB kazanımı +
   çıkmış soru önerisi + mini quiz akışı
2. `urun-2-deneme-netleri.png` — 10 saniyelik ders bazlı net girişi
3. `urun-3-analiz-panosu.png` — güven aralıklı ustalık haritası + öncelik listesi + net gidişatı
4. `urun-4-haftalik-plan.png` — süpervizör üzerinden üretilen haftalık plan
5. `api-docs.png` — FastAPI otomatik dokümantasyonu (tüm uçlar)

Teknik durum: **30 otomatik test + lint, GitHub Actions'ta her push'ta koşuyor ve yeşil.**

## Sprint Review — 19 Temmuz [toplantı sonrası kesinleşecek]

Taslak gündem:
- Canlı demo: soru fotoğrafı → anlatım → quiz → haritanın güncellenişi; koçtan plan isteme
- Doğruluk raporunun sunumu (%83.3 ve yöntem)
- Sprint 3 önceliklendirmesi: A5 (net tahmin modeli), T6 (kendi sınıflandırıcımız), taşınan
  C2/C3, kalıcı hafıza (B5), deploy (D4), video

Katılımcılar: [toplantıda doldurulacak]
Kararlar: [toplantıda doldurulacak]

## Sprint Retrospective [toplantı sonrası kesinleşecek — taslak maddeler]

**İyi gidenler:**
- Teknik hedeflerin %88'i tamamlandı; ölç→iyileştir→doğrula döngüsü kanıtla kapandı
- PR + gözden geçirme kültürü kuruldu ve iki PR'da sorunsuz işledi
- Test kapsamı 12'den 30'a çıktı, CI kesintisiz yeşil kaldı

**Geliştirilecekler:**
- Süreç belgeleri (daily, board) kodun gerisinde kaldı
- Görev sahiplenmede boşluklar oluştu (sahipsiz kalan paketler geç fark edildi)
- Takım üyesi kaybı sprint sonunda netleşti; erken sinyaller konuşulmalıydı

**Aksiyonlar:**
- [ ] Sprint 3'te board ve daily sorumlusu: Bahar; her akşam kısa yazılı daily
- [x] Ece'nin ayrılışı akademiye bildirildi (SM)
- [ ] C2/C3'ün sprint kapanışına kadar tamamlanması (Bahar)
