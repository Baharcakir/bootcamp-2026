"""Çarpan Streamlit arayüzü — Sprint 2 cilası.

Çekirdek döngü: soru sor → anlatım al → quiz çöz → harita kendiliğinden oluşsun.

Çalıştırma:
    uvicorn app.main:app --reload --app-dir backend   # önce API
    streamlit run frontend/streamlit_app.py --server.address 0.0.0.0  # telefon erişimi için

Öğrenci konu bazlı veri GİRMEZ: çözemediği sorunun fotoğrafını gönderir, konu etiketini
yapay zeka koyar. Denemeden yalnızca ders bazında net girilir (4-5 satır, ~10 saniye).

Sprint 2 değişiklikleri:
- Mobil UX: sidebar auto başlangıç, kamera akışı iyileştirmesi, tablo sadeleştirme
- Pano: ders bazlı ayrı net çizgileri (hangi ders varsa hepsi), haftalık plan görünümü
- Quiz arayüzü: anlatımdan sonra benzer soru, cevap haritaya işlenir
- Grafik: yatay bar + renk gradient + okunabilirlik
- Derin Bağlantı (Deep Linking): query params ile sayfa yönlendirmesi
"""

import os
from datetime import date

import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

API_URL = os.getenv("CARPAN_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Çarpan — TYT Koçu",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="auto",  # masaüstünde açık, mobilde collapsed
)

# ── Minimal CSS: mobil dostu buton ve metrikler ──────────────────────────────
st.markdown(
    """
    <style>
    /* Geniş buton stilleri */
    .stButton > button { width: 100%; border-radius: 10px; font-size: 1rem; }
    /* Metrik kutuları — mobilde küçük kalmasın */
    [data-testid="metric-container"] { background: #f0f4ff; border-radius: 10px; padding: 8px; }
    /* Koç sohbeti yüksekliği */
    .stChatFloatingInputContainer { bottom: 0; }
    /* Tablo kaydırma — yatay scroll mobilde */
    [data-testid="stDataFrame"] { overflow-x: auto; }
    /* Quiz şıkları daha büyük */
    .stRadio label { font-size: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── API yardımcı fonksiyonlar ────────────────────────────────────────────────

def api_get(path: str, **params):
    try:
        resp = httpx.get(f"{API_URL}{path}", params=params or None, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        st.error(f"API hatası ({API_URL}{path}): {exc}. Backend çalışıyor mu?")
        st.stop()


def api_post(
    path: str,
    payload: dict | None = None,
    files: dict | None = None,
    data: dict | None = None,
    silent: bool = False,
):
    try:
        resp = httpx.post(
            f"{API_URL}{path}", json=payload, files=files, data=data, timeout=180
        )
        if resp.status_code in (422, 503):
            if not silent:
                st.warning(resp.json().get("detail", "İstek işlenemedi"))
            return None
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as exc:
        if not silent:
            st.error(f"API hatası: {exc}")
        return None


# ── Kenar çubuğu: sayfa ve öğrenci seçimi ───────────────────────────────────
PAGES = ["📸 Soru Sor", "📝 Deneme Netleri", "📊 Analiz Panosu", "📅 Haftalık Plan", "💬 Koç Sohbeti"]

# Derin bağlantı (Deep Linking) entegrasyonu
_page_param = st.query_params.get("page", "")
_default_page = int(_page_param) if _page_param.isdigit() and int(_page_param) < len(PAGES) else 0

with st.sidebar:
    st.title("🎯 Çarpan")
    page = st.radio(
        "Sayfa seç",
        PAGES,
        index=_default_page,
        label_visibility="collapsed",
    )
    st.divider()

    students = api_get("/students")
    student = None
    if students:
        student = st.selectbox(
            "Öğrenci",
            students,
            format_func=lambda s: s["name"],
        )

    with st.expander("➕ Yeni öğrenci ekle"):
        with st.form("new_student"):
            name = st.text_input("İsim")
            goal = st.text_input("Hedef (ör. Tıp — ilk 30 bin)")
            exam_date = st.date_input("Sınav tarihi", value=date(2027, 6, 19))
            weekly_hours = st.number_input("Haftalık çalışma saati", 1, 80, 20)
            if st.form_submit_button("Kaydet", use_container_width=True) and name:
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
    st.info("👈 Başlamak için kenar çubuğunu açıp yeni bir öğrenci ekleyin.")
    st.stop()

sid = student["id"]

# ── SAYFA 1: Soru Sor ────────────────────────────────────────────────────────
if page == "📸 Soru Sor":
    st.header("📸 TYT Matematik sorusunu gönder")
    st.caption(
        "Eğitmen adım adım anlatır; soru konu etiketiyle zayıflık haritana otomatik işlenir — "
        "sen hiçbir şey etiketlemezsin. (v1: TYT Matematik + Geometri)"
    )

    tab_upload, tab_camera = st.tabs(["📁 Fotoğraf yükle", "📷 Kameradan çek"])
    with tab_upload:
        uploaded = st.file_uploader(
            "Soru fotoğrafı", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed"
        )
    with tab_camera:
        captured = st.camera_input("Soruyu kameraya gösterip çek", label_visibility="collapsed")
    photo = uploaded if uploaded is not None else captured

    text = st.text_area(
        "veya soruyu / takıldığın yeri yaz",
        placeholder="Fotoğraf yerine soruyu buraya da yazabilirsin...",
        height=100,
    )

    # Quiz durumunu session state'te sakla
    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {}  # {sid: {topic, question, choices, answer_index, explanation, answered}}

    col_btn, _ = st.columns([2, 3])
    with col_btn:
        ask_clicked = st.button(
            "🧑‍🏫 Anlat",
            type="primary",
            disabled=not (photo or text.strip()),
            use_container_width=True,
        )

    if ask_clicked:
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
            if result.get("in_scope"):
                # Yeni anlatım gelince eski quiz durumunu temizleyip bu konuyla ilklendir
                st.session_state.quiz_state[sid] = {
                    "topic": result["topic"],
                    "question": None,
                    "choices": [],
                    "answer_index": -1,
                    "explanation": "",
                    "answered": False,
                    "is_fallback": False,
                }
                st.session_state[f"quiz_open_{sid}"] = True
            else:
                st.session_state.pop(f"quiz_open_{sid}", None)

    # Anlatım sonucu ve kazanım referanslarını göster
    ask = st.session_state.get(f"ask_{sid}")
    if ask and ask.get("in_scope"):
        st.success(f"🏷️ **{ask['subject']} / {ask['topic']}** olarak haritana işlendi")
        st.markdown(ask["explanation"])
        
        # MEB kazanım referansı (T2)
        if ask.get("kaynak"):
            st.info(f"📚 **Kazanım Referansı:** {ask['kaynak']}")
        
        # Çıkmış soru benzerleri (T2)
        if ask.get("benzer_sorular"):
            st.caption("🔗 **Bu konudan çıkmış benzer sorular:** " + " · ".join(ask["benzer_sorular"]))

        # ── Mini Quiz Bölümü (T3) ─────────────────────────────────────────────
        quiz_st = st.session_state.quiz_state.get(sid)
        if quiz_st and st.session_state.get(f"quiz_open_{sid}"):
            st.divider()
            st.subheader("🔁 Benzer Soru — Mini Quiz")

            if quiz_st["question"] is None:
                # Henüz soru üretilmemiş → üret
                with st.spinner(f"**{quiz_st['topic']}** konusunda benzer soru hazırlanıyor..."):
                    qdata = api_get(f"/students/{sid}/quiz", topic=quiz_st["topic"])

                if qdata:
                    # Quiz API'si secenekler dict (A, B, C...) veya choices list dönebilir
                    # Görkem'in doğrulanmış quizi: secenekler: {"A": "10", "B": "12"...} ve dogru: "B"
                    choices_dict = qdata.get("secenekler")
                    if choices_dict:
                        choices_list = [f"{h}) {choices_dict[h]}" for h in sorted(choices_dict.keys())]
                        correct_key = qdata.get("dogru", "A")
                        # Harfe karşılık gelen index'i bul
                        correct_idx = sorted(choices_dict.keys()).index(correct_key)
                    else:
                        choices_list = qdata.get("choices", [])
                        correct_idx = qdata.get("answer_index", 0)

                    quiz_st["question"] = qdata.get("soru") or qdata.get("question")
                    quiz_st["choices"] = choices_list
                    quiz_st["answer_index"] = correct_idx
                    quiz_st["explanation"] = qdata.get("cozum") or qdata.get("explanation", "")
                    quiz_st["is_fallback"] = qdata.get("is_fallback", False)

            if quiz_st["question"]:
                if quiz_st.get("is_fallback"):
                    st.caption("⚡ Örnek soru (API key tanımlı olunca Gemini'den üretilir)")
                st.markdown(f"**{quiz_st['question']}**")

                if not quiz_st["answered"]:
                    selected = st.radio(
                        "Cevabını seç:",
                        quiz_st["choices"],
                        index=None,
                        key=f"quiz_radio_{sid}",
                    )
                    col_ans, _ = st.columns([2, 3])
                    with col_ans:
                        if st.button(
                            "✅ Cevapla",
                            disabled=selected is None,
                            use_container_width=True,
                            key=f"quiz_submit_{sid}",
                        ):
                            sel_idx = quiz_st["choices"].index(selected)
                            # Backend'e event ekle (T3)
                            dogru_mu = (sel_idx == quiz_st["answer_index"])
                            api_post(
                                f"/students/{sid}/quiz/answer",
                                payload={
                                    "topic": quiz_st["topic"],
                                    "selected_index": sel_idx,
                                    "correct_index": quiz_st["answer_index"],
                                },
                            )
                            quiz_st["answered"] = True
                            quiz_st["sel_idx"] = sel_idx
                            st.rerun()
                else:
                    sel_idx = quiz_st.get("sel_idx", -1)
                    correct_idx = quiz_st["answer_index"]
                    if sel_idx == correct_idx:
                        st.success("✅ Doğru! Ustalık haritana başarı olarak işlendi.")
                    else:
                        correct_choice = quiz_st["choices"][correct_idx] if correct_idx >= 0 else "?"
                        st.error(f"❌ Yanlış. Doğru cevap: **{correct_choice}**")
                    st.info(f"💡 {quiz_st['explanation']}")

                    col_r, _ = st.columns([2, 3])
                    with col_r:
                        if st.button("🔄 Yeni Soru", use_container_width=True, key=f"quiz_reset_{sid}"):
                            quiz_st["question"] = None
                            quiz_st["answered"] = False
                            quiz_st.pop("sel_idx", None)
                            st.rerun()

    elif ask:
        st.info(ask["explanation"])  # kapsam dışı

    st.divider()

    # ── Fotoğrafsız takılma işareti ─────────────────────────────────────────
    with st.expander("😵 Fotoğraf yok — takıldığın konuyu işaretle"):
        topics = api_get("/topics")
        scope = set(topics.get("tutor_scope", []))
        subjects_in_scope = [s for s in topics["subjects"] if s["name"] in scope]
        subject_sel = st.selectbox("Ders", [s["name"] for s in subjects_in_scope], key="manual_subject")
        topic_list = next(s["topics"] for s in subjects_in_scope if s["name"] == subject_sel)
        topic_sel = st.selectbox("Konu", topic_list, key="manual_topic")
        if st.button("📌 Bu konuda takıldım", use_container_width=True):
            if api_post(
                f"/students/{sid}/events",
                payload={"subject": subject_sel, "topic": topic_sel, "succeeded": False},
            ):
                st.success("İşlendi — haritan güncellendi")

    # ── Son sinyaller ───────────────────────────────────────────────────────
    events = api_get(f"/students/{sid}/events", limit=8)
    if events:
        st.subheader("Son sinyaller")
        df = pd.DataFrame(events)[["happened_on", "topic", "succeeded"]]
        df.columns = ["Tarih", "Konu", "Başarılı"]
        df["Başarılı"] = df["Başarılı"].map({True: "✅", False: "❌"})
        st.dataframe(df, hide_index=True, use_container_width=True)


# ── SAYFA 2: Deneme Netleri ─────────────────────────────────────────────────
elif page == "📝 Deneme Netleri":
    st.header("📝 Deneme Netleri")
    st.caption(
        "Sadece ders bazında toplam — konu kırılımı istemiyoruz, onu sorular halleder. "
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
    edited = st.data_editor(editor_df, hide_index=True, use_container_width=True)

    if st.button("💾 Kaydet", type="primary", use_container_width=True):
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
        st.dataframe(df, hide_index=True, use_container_width=True)


# ── SAYFA 3: Analiz Panosu ──────────────────────────────────────────────────
elif page == "📊 Analiz Panosu":
    st.header(f"📊 {student['name']} — Analiz Panosu")

    # ── Konu Ustalık Haritası ────────────────────────────────────────────────
    mastery = api_get(f"/students/{sid}/mastery")

    if not mastery:
        st.info(
            "Haritan henüz boş — çözemediğin soruları 'Soru Sor' ekranından gönderdikçe "
            "burası kendiliğinden dolar."
        )
    else:
        df = pd.DataFrame(mastery)
        df = df.sort_values("mastery")  # en zayıf üstte (yatay bar'da solda)
        df["label"] = df["topic"]

        # Renk: mastery 0 → kırmızı, 0.5 → sarı, 1 → yeşil
        def mastery_color(m: float) -> str:
            r = int(255 * max(0, 1 - 2 * m))
            g = int(255 * max(0, min(1, 2 * m)))
            return f"rgb({r},{g},60)"

        colors = [mastery_color(m) for m in df["mastery"]]

        fig = go.Figure(
            go.Bar(
                y=df["label"],
                x=df["mastery"],
                orientation="h",
                marker_color=colors,
                error_x={
                    "type": "data",
                    "array": (df["ci_high"] - df["mastery"]).tolist(),
                    "arrayminus": (df["mastery"] - df["ci_low"]).tolist(),
                    "thickness": 1.5,
                    "width": 4,
                },
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Ustalık: %{x:.0%}<br>"
                    "<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            title="Konu Ustalık Haritası (%90 güven aralığıyla)",
            xaxis={"range": [0, 1], "title": "Ustalık", "tickformat": ".0%"},
            yaxis={"title": "", "automargin": True},
            height=max(400, len(df) * 40),
            margin={"l": 20, "r": 20, "t": 50, "b": 30},
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🔥 Öncelikli çalışılacak konular (İlk 10)")
        priorities = api_get(f"/students/{sid}/priorities", top=10)
        if priorities:
            pf = pd.DataFrame(priorities)
            # Güvenli sütun yeniden adlandırma
            col_map = {"subject": "Ders", "topic": "Konu", "mastery": "Ustalık", "priority": "Öncelik Skoru"}
            pf = pf.rename(columns=col_map)
            if "Ustalık" in pf.columns:
                pf["Ustalık"] = pf["Ustalık"].map(lambda x: f"%{x*100:.0f}")
            if "Öncelik Skoru" in pf.columns:
                pf["Öncelik Skoru"] = pf["Öncelik Skoru"].map(lambda x: f"{x:.2f}")
            st.dataframe(pf, hide_index=True, use_container_width=True)

    st.divider()

    # ── Net Gidişatı — Tüm Dersler Ayrı Çizgi ───────────────────────────────
    st.subheader("📈 Deneme Net Gidişatı")

    subject_trend = api_get(f"/students/{sid}/subject_trend")
    subjects_data = subject_trend.get("subjects", {})
    total_trend = api_get(f"/students/{sid}/trend")

    if not total_trend.get("history"):
        st.info("Deneme neti girildikçe gidişat grafiği burada oluşur.")
    else:
        fig2 = go.Figure()

        # Toplam TYT neti — kalın çizgi
        history_total = pd.DataFrame(total_trend["history"])
        fig2.add_trace(
            go.Scatter(
                x=history_total["taken_on"],
                y=history_total["net"],
                mode="lines+markers",
                name="Toplam TYT",
                line={"width": 3, "color": "#4a90d9"},
                marker={"size": 8},
            )
        )

        # Her ders için ince ayrı çizgi (veritabanında hangi ders varsa)
        SUBJECT_COLORS = {
            "Matematik": "#e74c3c",
            "Türkçe": "#2ecc71",
            "Fen Bilimleri": "#f39c12",
            "Sosyal Bilimler": "#9b59b6",
        }
        for subject, sdata in subjects_data.items():
            if not sdata.get("history"):
                continue
            hist = pd.DataFrame(sdata["history"])
            color = SUBJECT_COLORS.get(subject, "#888888")
            fig2.add_trace(
                go.Scatter(
                    x=hist["taken_on"],
                    y=hist["net"],
                    mode="lines+markers",
                    name=subject,
                    line={"width": 1.5, "color": color, "dash": "dot"},
                    marker={"size": 5},
                )
            )

        # Tahmin noktası
        if total_trend.get("predicted_next") is not None:
            last_date = history_total["taken_on"].iloc[-1]
            fig2.add_trace(
                go.Scatter(
                    x=[last_date],
                    y=[total_trend["predicted_next"]],
                    mode="markers",
                    marker={"symbol": "star", "size": 16, "color": "#f1c40f"},
                    name=f"Tahmin ~1 hafta ({total_trend['predicted_next']:.1f} net)",
                )
            )

        fig2.update_layout(
            xaxis_title="Tarih",
            yaxis_title="Net",
            legend={
                "orientation": "h",
                "y": -0.25,
                "x": 0,
                "xanchor": "left",
                "font": {"size": 11},
                "traceorder": "normal",
            },
            height=420,
            margin={"b": 100},  # legend için alt boşluk
        )
        st.plotly_chart(fig2, use_container_width=True)

        col_m1, col_m2 = st.columns(2)
        col_m1.metric(
            "Toplam Haftalık Eğilim",
            f"{total_trend['slope_per_week']:+.1f} net",
            help="Doğrusal eğilim (v0) — Sprint 3'te eğitilmiş modelle değişecek (A5)",
        )
        mat = subjects_data.get("Matematik")
        if mat and mat.get("slope_per_week") is not None:
            col_m2.metric(
                "Matematik Haftalık Eğilim",
                f"{mat['slope_per_week']:+.1f} net",
            )


# ── SAYFA 4: Haftalık Plan (Görkem/Emir Arda'nın B3 Bileşeni) ─────────────────
elif page == "📅 Haftalık Plan":
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
        st.dataframe(plan_df, hide_index=True, use_container_width=True)

        st.subheader("Konu öncelikleri")
        priorities_df = pd.DataFrame(plan["priorities"])
        if not priorities_df.empty:
            st.dataframe(priorities_df, hide_index=True, use_container_width=True)


# ── SAYFA 5: Koç Sohbeti ───────────────────────────────────────────────────
else:
    st.header(f"💬 Koç — {student['name']}")

    # API key uyarısı
    health_hint = st.empty()

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
        else:
            hint = (
                "⚠️ Koç şu an kullanılamıyor. GOOGLE_API_KEY gerekli — "
                "`.env` dosyasına ekle: https://aistudio.google.com/apikey"
            )
            st.session_state[chat_key].append(("assistant", hint))
            st.chat_message("assistant").write(hint)
