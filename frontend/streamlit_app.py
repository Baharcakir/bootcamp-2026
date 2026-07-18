"""Çarpan Streamlit arayüzü — çekirdek döngü: soru sor → anlatım al → harita kendiliğinden oluşsun.

Çalıştırma:
    uvicorn app.main:app --reload --app-dir backend   # önce API
    streamlit run frontend/streamlit_app.py           # sonra arayüz

Öğrenci konu bazlı veri GİRMEZ: çözemediği sorunun fotoğrafını gönderir, konu etiketini
yapay zeka koyar. Denemeden yalnızca ders bazında net girilir (4-5 satır).
"""

import os
from datetime import date

import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

API_URL = os.getenv("CARPAN_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Çarpan", page_icon="🎯", layout="wide")


def api_get(path: str, **params):
    try:
        resp = httpx.get(f"{API_URL}{path}", params=params or None, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        st.error(f"API hatası ({API_URL}{path}): {exc}. Backend çalışıyor mu?")
        st.stop()


def api_post(path: str, payload: dict | None = None, files: dict | None = None, data: dict | None = None):
    try:
        resp = httpx.post(f"{API_URL}{path}", json=payload, files=files, data=data, timeout=180)
        if resp.status_code in (422, 503):
            st.warning(resp.json().get("detail", "İstek işlenemedi"))
            return None
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        st.error(f"API hatası: {exc}")
        return None


# --- Kenar çubuğu: sayfa ve öğrenci seçimi ---
st.sidebar.title("🎯 Çarpan")
page = st.sidebar.radio(
    "Sayfa", ["📸 Soru Sor", "Deneme Netleri", "Analiz Panosu", "Haftalık Plan", "Koç Sohbeti"]
)

students = api_get("/students")
student = None
if students:
    student = st.sidebar.selectbox("Öğrenci", students, format_func=lambda s: s["name"])

with st.sidebar.expander("➕ Yeni öğrenci"):
    with st.form("new_student"):
        name = st.text_input("İsim")
        goal = st.text_input("Hedef (ör. Tıp — ilk 30 bin)")
        exam_date = st.date_input("Sınav tarihi", value=date(2027, 6, 19))
        weekly_hours = st.number_input("Haftalık çalışma saati", 1, 80, 20)
        if st.form_submit_button("Kaydet") and name:
            api_post(
                "/students",
                payload={
                    "name": name,
                    "goal": goal or None,
                    "exam_date": exam_date.isoformat(),
                    "weekly_hours": int(weekly_hours),
                },
            )
            st.rerun()

if not student:
    st.info("Başlamak için kenar çubuğundan yeni bir öğrenci ekleyin.")
    st.stop()

sid = student["id"]

# --- Sayfa 1: Soru Sor (çekirdek akış) ---
if page == "📸 Soru Sor":
    st.header("📸 Çözemediğin TYT Matematik sorusunu gönder")
    st.caption(
        "Eğitmen adım adım anlatır; soru, konu etiketiyle zayıflık haritana otomatik işlenir — "
        "sen hiçbir şey etiketlemezsin. (v1: TYT Matematik + Geometri; diğer dersler yolda)"
    )

    tab_upload, tab_camera = st.tabs(["📁 Fotoğraf yükle", "📷 Kameradan çek"])
    with tab_upload:
        uploaded = st.file_uploader("Soru fotoğrafı", type=["png", "jpg", "jpeg", "webp"])
    with tab_camera:
        captured = st.camera_input("Soruyu kameraya gösterip çek")
    photo = uploaded if uploaded is not None else captured

    text = st.text_area(
        "veya soruyu / takıldığın yeri yaz",
        placeholder="Fotoğraf yerine soruyu buraya da yazabilirsin (fotoğrafa not da ekleyebilirsin)...",
    )

    if st.button("🧑‍🏫 Anlat", type="primary", disabled=not (photo or text.strip())):
        files = None
        if photo:
            files = {
                "file": (
                    photo.name or "soru.jpg",
                    photo.getvalue(),
                    photo.type or "image/jpeg",
                )
            }
        with st.spinner("Eğitmen soruyu inceliyor..."):
            result = api_post(f"/students/{sid}/ask", files=files, data={"text": text or ""})
        if result:
            st.session_state[f"ask_{sid}"] = result
            st.session_state.pop(f"quiz_{sid}", None)  # yeni soru → eski quiz temizlenir

    ask = st.session_state.get(f"ask_{sid}")
    if ask and ask["in_scope"]:
        st.success(f"🏷️ **{ask['subject']} / {ask['topic']}** olarak haritana işlendi")
        st.markdown(ask["explanation"])
        if ask.get("kaynak"):
            st.caption(f"📚 {ask['kaynak']}")
        if ask.get("benzer_sorular"):
            st.caption("🔗 Bu konudan çıkmış sorular: " + " · ".join(ask["benzer_sorular"]))

        # --- T3: doğrulanmış mini quiz — doğru cevap haritayı YUKARI günceller ---
        quiz_key = f"quiz_{sid}"
        if st.button("🔁 Benzer soruyla kendini dene"):
            with st.spinner("Soru üretiliyor ve doğrulanıyor..."):
                quiz = api_post(f"/students/{sid}/quiz", payload={"topic": ask["topic"]})
            if quiz:
                quiz["cevaplandi"] = False
                st.session_state[quiz_key] = quiz

        quiz = st.session_state.get(quiz_key)
        if quiz:
            st.markdown(f"**Mini Quiz — {quiz['konu']}**")
            st.markdown(quiz["soru"])
            secim = st.radio(
                "Cevabın:",
                list(quiz["secenekler"]),
                format_func=lambda h: f"{h}) {quiz['secenekler'][h]}",
                index=None,
                key=f"secim_{sid}",
            )
            if st.button("Cevapla", disabled=secim is None or quiz["cevaplandi"]):
                dogru_mu = secim == quiz["dogru"]
                api_post(
                    f"/students/{sid}/events",
                    payload={"subject": "Matematik", "topic": quiz["konu"],
                             "succeeded": dogru_mu, "source": "quiz"},
                )
                quiz["cevaplandi"] = True
                quiz["dogru_mu"] = dogru_mu
                st.session_state[quiz_key] = quiz
            if quiz.get("cevaplandi"):
                if quiz.get("dogru_mu"):
                    st.success(f"Doğru! ✅ Haritanda **{quiz['konu']}** yukarı güncellendi.")
                else:
                    st.error(f"Yanlış — doğru cevap **{quiz['dogru']}**. Haritana işlendi.")
                with st.expander("Çözümü gör"):
                    st.markdown(quiz["cozum"])
    elif ask:
        st.info(ask["explanation"])  # kapsam dışı — nazik yönlendirme, kayıt düşmez

    with st.expander("Fotoğraf yok mu? Takıldığın konuyu tek dokunuşla işaretle"):
        topics = api_get("/topics")
        scope = set(topics.get("tutor_scope", []))
        subjects_in_scope = [s for s in topics["subjects"] if s["name"] in scope]
        subject = st.selectbox("Ders", [s["name"] for s in subjects_in_scope])
        topic_list = next(s["topics"] for s in subjects_in_scope if s["name"] == subject)
        topic = st.selectbox("Konu", topic_list)
        if st.button("😵 Bu konuda takıldım"):
            if api_post(
                f"/students/{sid}/events",
                payload={"subject": subject, "topic": topic, "succeeded": False},
            ):
                st.success("İşlendi — haritan güncellendi")

    events = api_get(f"/students/{sid}/events", limit=10)
    if events:
        st.subheader("Son sinyaller")
        df = pd.DataFrame(events)[["happened_on", "subject", "topic", "source", "succeeded"]]
        df.columns = ["Tarih", "Ders", "Konu", "Kaynak", "Başarılı"]
        st.dataframe(df, hide_index=True, width="stretch")

# --- Sayfa 2: Deneme Netleri (10 saniyelik giriş) ---
elif page == "Deneme Netleri":
    st.header("📝 Deneme Netleri")
    st.caption(
        "Sadece ders bazında toplam — konu kırılımı istemiyoruz, onu soruların halleder. "
        "Net takibi tüm TYT dersleri için; koçluk v1'de Matematik odaklı."
    )

    col1, col2 = st.columns(2)
    exam_name = col1.text_input("Deneme adı", value="TYT Deneme")
    taken_on = col2.date_input("Tarih", value=date.today())

    topics = api_get("/topics")
    editor_df = pd.DataFrame(
        {
            "Ders": [s["name"] for s in topics["subjects"]],
            "Doğru": 0,
            "Yanlış": 0,
            "Boş": 0,
        }
    )
    edited = st.data_editor(editor_df, hide_index=True, width="stretch")

    if st.button("💾 Kaydet", type="primary"):
        results = [
            {
                "subject": row["Ders"],
                "correct": int(row["Doğru"]),
                "wrong": int(row["Yanlış"]),
                "blank": int(row["Boş"]),
            }
            for _, row in edited.iterrows()
            if row["Doğru"] + row["Yanlış"] + row["Boş"] > 0
        ]
        result = api_post(
            f"/students/{sid}/exams",
            payload={"name": exam_name, "taken_on": taken_on.isoformat(), "results": results},
        )
        if result:
            st.success(f"Kaydedildi ✅ Toplam net: **{result['net']}**")

    exams = api_get(f"/students/{sid}/exams")
    if exams:
        st.subheader("Geçmiş denemeler")
        df = pd.DataFrame(exams)[["taken_on", "name", "net"]]
        df.columns = ["Tarih", "Deneme", "Net"]
        st.dataframe(df, hide_index=True, width="stretch")

# --- Sayfa 3: Analiz Panosu ---
elif page == "Analiz Panosu":
    st.header(f"📊 {student['name']} — Analiz Panosu")
    mastery = api_get(f"/students/{sid}/mastery")

    if not mastery:
        st.info(
            "Haritan henüz boş — çözemediğin soruları 'Soru Sor' ekranından gönderdikçe "
            "burası kendiliğinden dolar."
        )
    else:
        df = pd.DataFrame(mastery)
        df["label"] = df["subject"] + " / " + df["topic"]
        fig = go.Figure(
            go.Bar(
                x=df["label"],
                y=df["mastery"],
                error_y={
                    "type": "data",
                    "array": df["ci_high"] - df["mastery"],
                    "arrayminus": df["mastery"] - df["ci_low"],
                },
            )
        )
        fig.update_layout(
            title="Konu Ustalık Haritası (%90 güven aralığıyla)",
            yaxis={"range": [0, 1], "title": "Ustalık"},
            xaxis={"title": ""},
        )
        st.plotly_chart(fig, width="stretch")

        st.subheader("🔥 Öncelikli çalışılacak konular")
        priorities = api_get(f"/students/{sid}/priorities", top=10)
        st.dataframe(pd.DataFrame(priorities), hide_index=True, width="stretch")

    st.subheader("📈 Net gidişatı")
    trend = api_get(f"/students/{sid}/trend")
    if not trend["history"]:
        st.info("Deneme neti girildikçe gidişat grafiği burada oluşur.")
    else:
        history = pd.DataFrame(trend["history"])
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(x=history["taken_on"], y=history["net"], mode="lines+markers", name="Net")
        )
        if trend["predicted_next"] is not None:
            fig2.add_trace(
                go.Scatter(
                    x=[history["taken_on"].iloc[-1]],
                    y=[trend["predicted_next"]],
                    mode="markers",
                    marker={"symbol": "star", "size": 14},
                    name="Tahmin (~1 hafta)",
                )
            )
        st.plotly_chart(fig2, width="stretch")
        st.metric(
            "Haftalık eğilim",
            f"{trend['slope_per_week']:+.1f} net",
            help="Doğrusal eğilim (v0) — Sprint 3'te eğitilmiş modelle değişecek (A5)",
        )

# --- Sayfa 4: Haftalık Plan ---
elif page == "Haftalık Plan":
    st.header(f"🗓️ {student['name']} — Haftalık Çalışma Planı")
    st.caption(
        "Plan; sınav tarihi, haftalık saat bütçesi ve zayıflık haritasındaki konu "
        "önceliklerinden otomatik üretilir ve veritabanına kaydedilir."
    )

    if st.button("✨ Bu haftanın planını oluştur", type="primary"):
        with st.spinner("Planlayıcı uzman programı hazırlıyor..."):
            generated = api_post(f"/students/{sid}/plans/generate", payload={})
        if generated:
            st.success("Plan oluşturuldu ve kaydedildi.")
            st.rerun()

    plan = api_get(f"/students/{sid}/plans/latest")
    if not plan:
        st.info("Henüz plan yok. Yukarıdaki düğmeyle ilk haftalık planını oluştur.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Haftalık bütçe", f"{plan['weekly_hours']} saat")
        col2.metric("Toplam oturum", len(plan["items"]))
        remaining = plan.get("days_to_exam")
        col3.metric("Sınava kalan", f"{remaining} gün" if remaining is not None else "Belirtilmedi")
        st.info(plan["summary"])

        plan_df = pd.DataFrame(plan["items"])[
            ["day_name", "topic", "activity", "duration_minutes", "rationale"]
        ]
        plan_df.columns = ["Gün", "Konu", "Çalışma", "Süre (dk)", "Neden"]
        st.dataframe(plan_df, hide_index=True, width="stretch")

        st.subheader("Konu öncelikleri")
        priorities_df = pd.DataFrame(plan["priorities"])
        if not priorities_df.empty:
            st.dataframe(priorities_df, hide_index=True, width="stretch")

# --- Sayfa 5: Koç Sohbeti ---
else:
    st.header(f"💬 Koç — {student['name']}")
    chat_key = f"chat_{sid}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    for role, msg in st.session_state[chat_key]:
        st.chat_message(role).write(msg)

    if prompt := st.chat_input("Koçuna sor: Nerelerde zayıfım? Bu hafta ne çalışayım?"):
        st.session_state[chat_key].append(("user", prompt))
        st.chat_message("user").write(prompt)
        with st.spinner("Koç düşünüyor..."):
            result = api_post(f"/students/{sid}/chat", payload={"message": prompt})
        if result:
            st.session_state[chat_key].append(("assistant", result["reply"]))
            st.chat_message("assistant").write(result["reply"])
