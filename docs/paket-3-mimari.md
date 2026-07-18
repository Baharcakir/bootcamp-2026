# Paket 3 - Agent Mimarisi ve Haftalık Plan

## 1. Yönlendirme stratejisi

Koordinatörün kritik yönlendirme kararı `agents/routing.py` içinde saf bir fonksiyonla verilir. Böylece model sürümü, sıcaklık veya API kesintisi plan isteğinin yanlış uzmana gitmesine neden olmaz.

| Örnek istek | Rota |
|---|---|
| “Nerelerde zayıfım?” | analyst |
| “Netlerim nasıl gidiyor?” | analyst |
| “Bu hafta ne çalışayım?” | planner |
| “Bana haftalık program yap.” | planner |
| “Çarpanlara ayırmayı anlat.” | tutor |

Supervisor, LangGraph `StateGraph` üzerinde conditional edge ile seçilen tek node'a gider.

## 2. Uzmanlar

### Analist

ReAct agent olarak çalışır ve yalnızca veri araçlarını kullanır:

- `ogrenci_profili`
- `konu_analizi`
- `net_gidisati`

### Planlayıcı

Plan üretimi ve DB yazımı kritik olduğu için deterministik servis node'udur. LLM'in geçersiz JSON üretmesi, süre toplamını bozması veya planı kaydetmeyi unutması engellenir.

Girdiler:

- `Student.exam_date`
- `Student.weekly_hours`
- Bayesçi ustalık haritasından türetilen konu öncelikleri

Çıktı:

- `WeeklyPlanOut` Pydantic modeli
- Gün, konu, etkinlik, dakika ve gerekçe içeren oturumlar

Kurallar:

- Toplam dakika tam olarak `weekly_hours * 60` olur.
- Oturum sayısı 3-14 aralığında tutulur.
- Öncelik skorları oturum sayılarına ağırlıklı dağıtılır.
- Aynı konu mümkün olduğunca arka arkaya gelmez.
- Veri yoksa temel TYT Matematik konularıyla teşhis planı oluşturulur.

### Eğitmen

TYT Matematik kavram ve soru anlatımına odaklanan ayrı sistem prompt'u ile çalışır.

## 3. Hafıza

Parent supervisor graph `MemorySaver` ile derlenir. API çağrısında:

```python
config = {"configurable": {"thread_id": f"student-{student_id}"}}
```

kullanılır. Böylece aynı öğrenciye ait geçmiş kullanıcı ve uzman mesajları sonraki çağrıda state'e eklenir.

## 4. Veritabanı

### StudyPlan

- öğrenci
- hafta başlangıcı
- oluşturma tarihi
- sınav tarihi snapshot'ı
- haftalık saat ve toplam dakika
- özet
- konu öncelikleri JSON snapshot'ı
- aktif/pasif durumu

### StudyPlanItem

- plan ilişkisi
- sıra ve gün
- ders / konu
- çalışma etkinliği
- dakika
- öncelik gerekçesi

Yeni plan üretildiğinde önceki aktif planlar pasif hale getirilir. Geçmiş planlar silinmez.

## 5. API ve pano

`plans.py` router'ı plan üretme, son planı okuma ve geçmiş planları listeleme uçlarını sağlar. Streamlit'e yeni **Haftalık Plan** sayfası eklenmiştir. Sayfa planı üretir, DB'den tekrar okur ve tablo halinde gösterir.

## 6. Test edilebilirlik

`build_supervisor_graph()` uzman node'larını dependency injection ile alır. Yönlendirme testlerinde Gemini çağrısı yapılmadan sahte uzmanlar kullanılabilir. Planlama servisi de LLM'den bağımsız olduğu için deterministik test edilir.
