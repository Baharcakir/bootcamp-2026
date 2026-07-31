# **Takım İsmi**

Takım 76

# Ürün İle İlgili Bilgiler

## Takım Elemanları

- Emir Arda Tomaç: Product Owner
- Bahar Çakır: Scrum Master
- Görkem Çetinkaya: Team Member/Developer
- Doğa Alışkan: Team Member/Developer
- Ece Nur Şahin: Team Member/Developer *(19 Temmuz 2026'da bootcamp'ten ayrıldı)*

## Ürün İsmi

--Çarpan--

## Ürün Açıklaması

- Çarpan uygulaması, YKS dönemindeki öğrencilere destek amacıyla oluşturulmuş ve öğrencilerin takıldıkları soruları atıp yardım alabileceği, zayıf noktalarını belirleyebileceği ve kişiselleştirilmiş bir anlatıma olanak sağlayan bir uygulamadır.

## Ürün Özellikleri

- Soru fotoğraflarından adım adım soru çözümü
- Anlatımlardan sonra pekiştirmek amaçlı benzer soru çözümü
- Çözülemeyen sorulardan oluşturulan zayıflık haritası
- Haftalık kişisel çalışma planı
- Gelecek denemelerdeki başarı tahminleri
- AI koçuyla konuşabilme 



## Hedef Kitle

- YKS'ye hazırlanan öğrenciler
- Deneme netlerini arttırmak isteyen öğrenciler
- 15-25 yaş arası kullanıcılar


## Product Backlog URL

[Miro Backlog Board](https://miro.com/app/board/uXjVH-ttQY8=/?share_link_id=525660778806)

---

# Sprint 1

- **Backlog düzeni ve Story seçimleri**: Backlog'umuz ilk yapılacak story'lere göre düzenlenmiştir. Sprint başına tahmin edilen puan sayısını geçmeyecek şekilde sıradan seçimler yapılmaktadır. Story başına çıkan tahmin puanı, toplam puanın yarısından az tutulmuştur. 

Story'ler yapılacak işlere (task'lere) bölünmüştür. Miro Board'da gözüken kırmızı item'lar yapılacak işleri (task) gösterirken, mavi item'lar story'leri temsil etmektedir.

- **Daily Scrum**: Daily Scrum toplantılarının zamansal sebeplerden ötürü Slack üzerinden yapılmasına karar verilmiştir. Daily Scrum toplantısı örneği jpeg veya word olarak Readme'de tarafımızdan paylaşılmaktadır: [Sprint 1 Daily Scrum Chats](https://github.com/OyunveUygulamaAkademisi/BootcampScrumTemplate/blob/main/ProjectManagement/Sprint1Documents/DailyScrumMeetingNotesSprint1.docx?raw=true)

- **Sprint board update**: Sprint board screenshotları: 
![Backlog 1](Sprint1/backlog1.png)
![Backlog 2](Sprint1/backlog2.png)
![Backlog 3](Sprint1/backlog3.png)
![Backlog 4](Sprint1/backlog4.png)

- **Ürün Durumu**: Ekran görüntüleri:
  
  <img src="Sprint1/products1.png" alt="Sprint 1 Products" width="300">
  <img src="Sprint1/products2.png" alt="Sprint 1 Products" width="300">
  <img src="Sprint1/products3.png" alt="Sprint 1 Products" width="300">
  <img src="Sprint1/products4.png" alt="Sprint 1 Products" width="300">
  <img src="Sprint1/products5.png" alt="Sprint 1 Products" width="300">
  <img src="Sprint1/products6.png" alt="Sprint 1 Products" width="300">

- **Sprint Review**: 
Alınan kararlar: Veritabanı için gerekli olan TYT örnek sorularının toplanması gerekmektedir. Kişiselleştirilmiş öğrenme asistanı için fine-tuning işlemine gerek olmadığına ve aynı sonucun Gemini API ve RAG yöntemiyle ulaşılabileceğine karar verilmiştir.

- **Sprint Retrospective:**
  - Takım içindeki görev dağılımıyla ilgili düzenleme yapılması kararı alınmıştır
  - Makine öğrenmesi modellerinin eğitimiyle ilgili tüm ekip üyelerinin araştırma yapması kararı alınmıştır

---

# Sprint 2

- **Sprint Notları**: Sprint hedefi, ürünün çekirdek döngüsünü uçtan uca kapatmak ve kalitesini ölçmekti: soru fotoğrafından adım adım anlatım + otomatik konu etiketi, MEB kazanımına dayalı kaynak gösterimi ve benzer çıkmış soru önerisi, doğrulanmış mini quiz, sentetik öğrenci verisiyle kalibre edilen ustalık modeli, süpervizör agent mimarisi ve haftalık çalışma planı. Sprint başında işler kişi başına görev paketleri halinde dağıtılmış; sprint ortasında kod işbirliği dal + Pull Request + gözden geçirme düzenine geçirilmiştir (PR #1, PR #2). Ayrıntılı uygulama notları: [Sprint 2 detay raporu](Sprint2/Takım76-Sprint2-README.md)

- **Takım Değişikliği**: Ece Nur Şahin sprint sonunda bootcamp'ten ayrılmıştır; durum akademiye Scrum Master tarafından bildirilmiştir ve takım 4 kişiyle devam etmektedir. Ayrılan üyenin süreç işleri Görkem'e, arayüz işleri Bahar'a devredilmiştir.

- **Tahmin Edilen Tamamlanacak Puan**: Sprint 2 planı 64 puandır; sprint kapanışında tüm 64 puan tamamlanmıştır.

| Story | Puan | Durum | Katkıda Bulunan |
|---|---|---|---|
| T2 — Kaynaklı anlatım (MEB kazanımı + çıkmış soru önerisi) | 8 | ✅ | Görkem |
| T3 — Doğrulanmış quiz + ustalık güncelleme döngüsü | 8 | ✅ | Görkem |
| T4 — ÖSYM değerlendirme seti + doğruluk raporu | 5 | ✅ | Görkem |
| A3 — Sentetik öğrenci üreteci | 8 | ✅ | Doğa |
| A4 — Ustalık modeli kalibrasyonu | 8 | ✅ | Doğa |
| B2 — Süpervizör agent mimarisi | 5 | ✅ | Emir Arda |
| B3 — Haftalık çalışma planı | 8 | ✅ | Emir Arda |
| D3 — Test kapsamının genişletilmesi (12 → 30 test) | 4 | ✅ | Görkem |
| E2 — Sprint 2 teslim seti | 2 | ✅ | Görkem |
| C2 — Soru sorma mobil deneyim turu + quiz arayüzü | 3 | ✅ | Bahar |
| C3 — Panoda ders bazlı net gidişatı + pano cilası | 5 | ✅ | Bahar |

- **Öne Çıkan Ölçüm**: Otomatik konu etiketleme, 120 gerçek ÖSYM sorusundan (2024-2026 TYT) oluşan elle etiketli sette ölçülmüştür; uyuşmazlık denetimi ve prompt'a eklenen tutarlılık kurallarıyla doğruluk **%76.7 → %80.8 → %83.3** olarak iyileştirilmiştir. Yöntem, sistematik hata analizi ve denetim izleri: [etiketleme doğruluk raporu](../docs/etiketleme-dogruluk-raporu.md)

- **Daily Scrum**: Bu sprintte daily ritmi düzenli işlememiş, koordinasyon büyük ölçüde Pull Request açıklamaları ve birebir mesajlaşma üzerinden yürümüştür; bu durum retrospektifte iyileştirme maddesi olarak ele alınmıştır. Sprint boyunca tutulan notların derlemesi: [Sprint 2 Daily Scrum Notları](Sprint2/DailyScrumMeetingNotesSprint2.docx)

- **Sprint board update**: Sprint board screenshotları:
![Backlog 1](Sprint2/backlog1.png)
![Backlog 2](Sprint2/backlog2.png)
![Backlog 3](Sprint2/backlog3.png)

- **Ürün Durumu**: Ekran görüntüleri (soru sorma akışı, deneme neti girişi, konu bazlı renk gradyanlı ustalık haritası, ders bazlı net gidişatı ve haftalık plan). 30 otomatik test + lint her push'ta GitHub Actions üzerinde koşmaktadır.

  <img src="Sprint2/sprint2_soru_sor.png" alt="Sprint 2 Soru Sor" width="300">
  <img src="Sprint2/sprint2_deneme_netleri.png" alt="Sprint 2 Deneme Netleri" width="300">
  <img src="Sprint2/sprint2_analiz_panosu.png" alt="Sprint 2 Analiz Panosu" width="300">
  <img src="Sprint2/sprint2_net_gidisati.png" alt="Sprint 2 Net Gidişatı" width="300">
  <img src="Sprint2/sprint2_koc_sohbeti.png" alt="Sprint 2 Koç Sohbeti" width="300">

- **Sprint Review**: 
Canlı demo: soru fotoğrafı → anlatım → quiz → zayıflık haritasının güncellenişi → koçtan haftalık plan. Doğruluk raporunun sunumu (%83.3) ve Sprint 3 önceliklendirmesi planlanmıştır.
Katılımcılar: Bahar, Görkem, Doğa, Emir Arda
Alınan kararlar: API key olmadan ürünün demo modunda çalışmaya devam etmesi jüri sunumu için kritik olduğu görülmüştür ve fallback mekanizması hayata geçirilmiştir. Subject trend endpoint generic yazıldı — ilerleyen sprintlerde yeni ders eklenmesi halinde kod değişmeyecek.

- **Sprint Retrospective:**
  - Teknik hedeflerin tamamı kapatılmış, ölç → iyileştir → doğrula döngüsü kanıtıyla tamamlanmıştır
  - Dal + Pull Request + gözden geçirme kültürü kurulmuştur; test kapsamı 12'den 30'a çıkmıştır
  - Süreç belgeleri (daily, board) kodun gerisinde kalmıştır; Sprint 3'te board ve daily sorumlusu Bahar olacak, her akşam kısa yazılı daily tutulacaktır
  - Görev sahiplenmedeki boşlukların erken konuşulması kararlaştırılmıştır
  - Streamlit'in mobil deneyimi sınırlı kalmaktadır; Sprint 3'te PWA veya farklı frontend framework değerlendirilebilir

---

# Sprint 3

- **Sprint Notları**: Sprint hedefi, Sprint 2'de kanıtlanan çekirdek döngüyü jüri önünde savunulabilir kılmak ve final teslimi tamamlamaktı: kendi eğittiğimiz konu sınıflandırıcısı (T6), GradientBoosting net tahmin modeli (A5), karne fotoğrafından otomatik net okuma (T5), koç agent kalıcı hafızası (B4) ve eğitim verisi altyapısının tamamlanması. Ayrıntılı uygulama notları: [Sprint 3 detay raporu](Sprint3/Takım76-Sprint3-README.md)

- **Tahmin Edilen Tamamlanacak Puan**: Sprint 3 planı 58 puandır; sprint kapanışında tüm 58 puan tamamlanmıştır.

| Story | Puan | Durum | Katkıda Bulunan |
|---|---|---|---|
| T5 — Karne fotoğrafından net okuma | 8 | ✅ | Bahar |
| T6 — Kendi konu sınıflandırıcısını eğit ve karşılaştır | 8 | ✅ | Görkem |
| T7 — Sınıflandırıcıyı `/ask` akışına entegre et | 5 | ✅ | Görkem |
| A5 — GradientBoosting net tahmin modeli | 8 | ✅ | Doğa |
| A6 — Panoda net gidişatı + bir sonraki deneme kestirimi | 3 | ✅ | Doğa |
| B4 — Koç agent kalıcı hafıza (SQLite) | 5 | ✅ | Emir Arda |
| B5 — Agent araç zenginleştirmesi | 3 | ✅ | Emir Arda |
| D4 — Canlı ürün deploymenti | 5 | ✅ | Emir Arda |
| E3 — Sprint 3 teslim seti | 5 | ✅ | Bahar |
| E4 — Daily & board canlı tutma | 3 | ✅ | Bahar |
| Q1 — Eğitim verisi altyapısı (transkripsiyon + üretim) | 5 | ✅ | Görkem |

- **Öne Çıkan Ölçümler**:
  - **Kendi sınıflandırıcımız:** TF-IDF + LogReg modeli aynı 120 soruluk ÖSYM setinde **%58.3** doğruluk; Gemini zero-shot **%83.3**. Fark dürüstçe raporlandı. Asıl değeri: API key olmadan sistem çalışır, milisaniyede sonuç verir. [siniflandirici-karsilastirma.md](../docs/siniflandirici-karsilastirma.md)
  - **Net tahmin modeli:** GradientBoosting, sentetik kohortta baseline'ı geçti (**MAE 2.10 vs 3.17, ~%34 iyileşme**). Model sentetik ölçekte eğitildiği için henüz canlı veriye bağlanmadı; panodaki tahmin deneme geçmişinden hesaplanan kestirimdir. [net-tahmin.md](../docs/net-tahmin.md)
  - **Kalibrasyon:** Bayesçi ustalık modeli 1000 sentetik öğrenciyle kalibre edildi, MAE 0.1021. [kalibrasyon.md](../docs/kalibrasyon.md)
  - **Eğitim verisi:** 317 AI üretimi soru (`data/uretilen_sorular.csv`), 1000 sentetik öğrenci profili (`data/synthetic_students.csv`)

- **Daily Scrum**: Sprint 3'te daily ritmi her akşam yazılı olarak toplanmıştır (Sprint 2 retrosunda söz verilen iyileştirme). Notların derlemesi: [Sprint 3 Daily Scrum Notları](Sprint3/DailyScrumMeetingNotesSprint3.md)

- **Sprint board update**: Sprint board ekran görüntüleri sprint tamamlandığında eklenecektir:

  > 📌 [Miro Backlog Board](https://miro.com/app/board/uXjVH-ttQY8=/?share_link_id=525660778806)

- **Ürün Durumu**: Sprint 3 sonu itibarıyla tüm özellikler entegre ve çalışır durumda: soru fotoğrafından anlatım + otomatik etiketleme (Gemini veya yerel model), karne fotoğrafından net okuma, Bayesçi ustalık haritası + net gidişatı kestirimi, kişisel haftalık plan, LangGraph koç agent (kalıcı hafıza). 38 otomatik test + lint her push'ta GitHub Actions üzerinde koşmaktadır.

  > Ekran görüntüleri çekilip `Sprint3/` klasörüne eklenecek.

- **Sprint Review**:
  Canlı demo: karne fotoğrafı → net okuma → soru fotoğrafı → anlatım (yerel sınıflandırıcı ile) → quiz → harita → koç → plan. Model kanıtlarının sunumu (T6 %58.3 karşılaştırma, A5 %34 iyileşme, A4 kalibrasyon).
  Katılımcılar: Bahar, Görkem, Doğa, Emir Arda.
  Alınan kararlar: Gemini vs. kendi modelimiz farkı (%83.3 vs %58.3) jüriye dürüstçe sunulacak; fallback mekanizması demo için kritik ve çalışır durumda; video senaryosu finallendi.

- **Sprint Retrospective:**
  - Teknik hedeflerin tamamı kapatıldı: kendi modellerimiz eğitildi, karşılaştırıldı ve entegre edildi
  - Süreç belgeleri (daily, board) Sprint 2 retrosunda söz verilen düzeye çıkarıldı
  - Eğitim verisi altyapısı sağlamlaştı: transkripsiyon, üretim ve eğitim pipeline'ları scriptlendi
  - Kendi modelimiz %58.3 ile Gemini'yi geçemedi — fark anlaşılır (27 sınıf, ~500 örnek); daha büyük veri ile kapatılabilir (post-bootcamp)
  - Streamlit mobil deneyimi hâlâ sınırlı; sonraki versiyonda PWA değerlendirilebilir

---