# Kabul Kontrol Listesi

## Agent ve orkestrasyon

- [x] Koordinatör + analist/planlayıcı/eğitmen LangGraph mimarisi
- [x] Conditional routing
- [x] Yönlendirme birim testleri
- [x] Yapılandırılmış plan çıktısı ve DB kaydı
- [x] Koç sohbetinden plan rotası

## Kalıcı hafıza

- [x] `MemorySaver` yerine SQLite `SqliteSaver`
- [x] Öğrenci bazlı `thread_id`
- [x] Uygulama kapat-aç senaryosunu test eden otomatik test
- [x] Öğrenciler arası hafıza izolasyonu testi
- [x] Checkpoint dizini/dosyası oluşturma testi
- [x] LLM anahtarsız manuel smoke script'i

## Canlıya alma

- [x] Railway `railway.json` başlangıç ve healthcheck ayarı
- [x] Kalıcı `/data` volume değişkenleri belgeli
- [x] Streamlit Community Cloud secret örneği
- [x] Görsel yükleme limiti 10 MB
- [ ] Railway API canlı URL'si README'ye yazıldı
- [ ] Streamlit canlı URL'si README'ye yazıldı
- [ ] Telefonla dış ağdan uçtan uca test tamamlandı
- [ ] Restart sonrası “dün hangi konuya çalışmıştık?” kabul testi tamamlandı

## Kalite

- [x] Pytest hafıza testleri eklendi
- [x] CI mevcut test/lint komutları yeni dosyaları kapsıyor
- [ ] GitHub Actions son çalışma yeşil
