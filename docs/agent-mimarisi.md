# Agent Mimarisi, Kalıcı Hafıza ve Canlıya Alma

## 1. Yönlendirme stratejisi

Koordinatörün kritik yönlendirme kararı `agents/routing.py` içinde saf bir fonksiyonla
verilir. Supervisor, LangGraph `StateGraph` üzerinde conditional edge ile yalnız seçilen
uzmana gider.

| Örnek istek | Rota |
|---|---|
| “Nerelerde zayıfım?” | analyst |
| “Bu hafta ne çalışayım?” | planner |
| “Çarpanlara ayırmayı anlat.” | tutor |

## 2. Uzmanlar

- **Analist:** `ogrenci_profili`, `konu_analizi`, `net_gidisati` araçlarını kullanan ReAct agent.
- **Planlayıcı:** Planı deterministik servisle üretir ve aynı işlemde veritabanına kaydeder.
- **Eğitmen:** TYT Matematik anlatımına odaklanan ayrı sistem prompt'u kullanır.

## 3. Kalıcı koç hafızası

Parent supervisor graph artık RAM tabanlı `MemorySaver` yerine
`langgraph-checkpoint-sqlite` paketindeki `SqliteSaver` ile derlenir.

```python
config = {"configurable": {"thread_id": f"student-{student_id}"}}
```

Her öğrenci ayrı thread kullanır. Checkpoint yolu `COACH_MEMORY_PATH` ile ayarlanır.
Yerel varsayılan `./data/coach-checkpoints.sqlite3`, Railway dağıtımında ise
`/data/coach-checkpoints.sqlite3` olur.

SQLite bağlantısında:

- `check_same_thread=False`
- `busy_timeout=5000`
- `journal_mode=WAL`
- eşzamanlı graph çağrıları için süreç içi kilit

kullanılır. Böylece küçük tek-instance demo dağıtımında checkpoint yazımları güvenli olur.

## 4. Kabul testleri

`backend/tests/test_persistent_memory.py` üç durumu doğrular:

1. Bağlantı ve graph tamamen kapatılıp tekrar açıldığında önceki oturum geri gelir.
2. Farklı öğrenci `thread_id` değerlerinin geçmişleri birbirine karışmaz.
3. Checkpoint dizini ve SQLite dosyası otomatik oluşturulur.

## 5. Kalıcı disk ve deploy

API Railway üzerinde çalışır ve `/data` yoluna volume bağlanır:

```text
DATABASE_URL=sqlite:////data/carpan.db
COACH_MEMORY_PATH=/data/coach-checkpoints.sqlite3
```

Arayüz Streamlit Community Cloud'da çalışır ve `CARPAN_API_URL` secret'ı ile API'ye
bağlanır. Ayrıntılı adımlar `docs/deploy.md` içindedir.

## 6. Plan veritabanı

`StudyPlan` ve `StudyPlanItem` yapısı korunur. Yeni plan üretildiğinde önceki aktif planlar
pasif hale getirilir; geçmiş planlar silinmez.
