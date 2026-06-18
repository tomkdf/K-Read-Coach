import html
import time
from pathlib import Path
import streamlit as st
from modules.data_loader import load_dataset, get_categories, get_sentences_by_category
from modules.asr_interface import transcribe_audio
from modules.comparison import compare_texts
from modules.feedback import generate_feedback

DATA_PATH = "data/k_read_coach_dataset.csv"
CLIPS_DIR = "data/clips"

# --- ТЕМА ОФОРМЛЕНИЯ ---
st.markdown("""
<style>
.stApp { background-color: #f5f0eb; }

.sentence-card {
    background-color: #e8e0d8;
    border-radius: 12px;
    padding: 24px;
    margin: 16px 0;
    font-size: 28px;
    text-align: center;
    font-weight: bold;
    color: #2c2c2c;
}

.stButton > button[kind="primary"] {
    background-color: #2c2c2c !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    height: 45px !important;
    font-weight: bold !important;
}

.stButton > button[kind="secondary"] {
    background-color: white !important;
    color: #2c2c2c !important;
    border: 2px solid #2c2c2c !important;
    border-radius: 8px !important;
    height: 45px !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return load_dataset(DATA_PATH)

df, is_real_dataset = load_data()

# --- ПАРАМЕТРЫ URL ---
query_params = st.query_params

url_category = query_params.get("category", None)
url_sentence = query_params.get("sentence", None)

with st.sidebar:
    st.title("K-Read Coach")
    st.caption("Практика разговорного корейского языка")

    if not is_real_dataset:
        st.warning("Используются тестовые данные — поместите k_read_coach_dataset.csv в папку data/")

    categories = get_categories(df)
    
    default_cat_idx = 0
    if url_category in categories:
        default_cat_idx = categories.index(url_category)
        
    selected_category = st.selectbox("ТЕМА", categories, index=default_cat_idx)

    sentences_df = get_sentences_by_category(df, selected_category)
    if sentences_df.empty:
        st.error("Для этой категории не найдено ни одного предложения.")
        st.stop()
        
    sentences_list = sentences_df["sentence"].tolist()
    
    default_sent_idx = 0
    if url_sentence in sentences_list:
        default_sent_idx = sentences_list.index(url_sentence)
        
    selected_sentence = st.selectbox("ПРЕДЛОЖЕНИЕ", sentences_list, index=default_sent_idx)


st.header("Практическое занятие")

row = sentences_df[sentences_df["sentence"] == selected_sentence].iloc[0]
target_sentence = row["sentence"]

# Affichage de la phrase (Simple, propre et sans HTML dynamique capricieux)
st.markdown(f'<div class="sentence-card">{html.escape(target_sentence)}</div>', unsafe_allow_html=True)

st.markdown(f"""
    <div style="background-color: #ffffff; padding: 14px 20px; border-radius: 8px; border-left: 5px solid #7f8c8d; margin-bottom: 10px;">
        <span style="color: #7f8c8d; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block; margin-bottom: 4px;">Перевод</span>
        <span style="font-size: 16px; color: #2c2c2c;">{html.escape(row['russian_translation'])}</span>
    </div>
""", unsafe_allow_html=True)

# Русское произношение корейского текста (выделенная контрастная плашка)
st.markdown(f"""
    <div style="background-color: #e0f2fe; padding: 14px 20px; border-radius: 8px; border-left: 5px solid #0284c7; margin-bottom: 20px;">
        <span style="color: #0369a1; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block; margin-bottom: 4px;">🗣️ Произношение (Транскрипция)</span>
        <span style="font-size: 18px; font-weight: bold; color: #0369a1;">{html.escape(row['russian_pronunciation'])}</span>
    </div>
""", unsafe_allow_html=True)

st.subheader("Эталонное произношение")
reference_audio_path = (Path(CLIPS_DIR) / row["path"]).resolve()
clips_base = Path(CLIPS_DIR).resolve()
if not str(reference_audio_path).startswith(str(clips_base)):
    st.error("Обнаружен некорректный путь к аудиофайлу.")
    st.stop()
if is_real_dataset and reference_audio_path.exists():
    st.audio(str(reference_audio_path))
elif is_real_dataset:
    st.warning(f"Аудиофайл не найден: {reference_audio_path}")
else:
    st.warning("Эталонное аудио недоступно в тестовом режиме.")

st.subheader("Ваше чтение")

if "audio_input_nonce" not in st.session_state:
    st.session_state["audio_input_nonce"] = 0

audio_bytes = None
recorded_audio = st.audio_input(
    "Нажмите, чтобы записать свое чтение",
    key=f"user_audio_{st.session_state['audio_input_nonce']}",
)
if recorded_audio is not None:
    audio_bytes = recorded_audio.getvalue()
    st.audio(audio_bytes, format=recorded_audio.type or "audio/wav")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    analyze_clicked = st.button("✨ Проверить произношение", type="primary", use_container_width=True)

with col2:
    retry_clicked = st.button("🔄 Сбросить", type="secondary", use_container_width=True)

if retry_clicked:
    st.session_state["audio_input_nonce"] += 1
    st.query_params.clear()
    st.rerun()

if analyze_clicked:
    if not audio_bytes:
        st.warning("Пожалуйста, сначала запишите свой голос!")
    else:
        try:
            with st.spinner("✨ K-Read Coach анализирует ваше произношение..."):
                upload_dir = Path("uploads")
                upload_dir.mkdir(exist_ok=True)
                path = str(upload_dir / f"user_audio_{int(time.time())}.wav")
                
                with open(path, "wb") as f:
                    f.write(audio_bytes)
                
                try:
                    recognized = transcribe_audio(path)
                    if not recognized:
                        st.warning("Мы не смогли вас расслышать. Пожалуйста, поднесите микрофон ближе!")
                        st.stop()
                    
                    # Estimation du temps basée sur la taille du fichier pour la fluidité
                    duration_seconds = len(audio_bytes) / 96000
                    if duration_seconds < 0.5:
                        duration_seconds = 1.0

                    # Calcul des scores
                    result = compare_texts(target_sentence, recognized, audio_duration=duration_seconds)
                    feedback = generate_feedback(result["score"])
                finally:
                    Path(path).unlink(missing_ok=True)

            # --- РЕЗУЛЬТАТЫ АНАЛИЗА ---
            st.success("🎉 Анализ завершен!")
            st.subheader("📊 Результаты проверки")
            
            st.markdown(f"""
                <div style="background-color: white; padding: 24px; border-radius: 12px; border: 1px solid #e8e0d8; margin-bottom: 20px;">
                    <p style="margin:0 0 8px 0; color:#7f8c8d; text-transform: uppercase; font-size:12px; font-weight:bold; letter-spacing:0.5px;">Что услышал тренер</p>
                    <p style="margin:0; font-size: 22px; font-weight: bold; color: #2c2c2c;">{result['recognized']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Affichage des deux colonnes : Prononciation et Fluidité
            col_pron, col_fluid = st.columns(2)
            
            with col_pron:
                st.markdown(f"""
                    <div style="background-color: #fcfbfa; padding: 16px; border-radius: 8px; border-left: 5px solid #3498db; text-align: center;">
                        <p style="margin:0; color:#7f8c8d; font-size:13px; font-weight:bold;">🗣️ Произношение</p>
                        <p style="margin:5px 0 0 0; font-size: 24px; font-weight: bold; color: #2980b9;">{result['pronunciation_score']:.0f} <span style="font-size:14px; color:#95a5a6;">/ 100</span></p>
                    </div>
                """, unsafe_allow_html=True)
                
            with col_fluid:
                rate = result['speech_rate']
                emoji_speed = "🐢" if rate < 2.0 else ("⚡" if rate > 4.0 else "🏃‍♂️")
                    
                st.markdown(f"""
                    <div style="background-color: #fcfbfa; padding: 16px; border-radius: 8px; border-left: 5px solid #2ecc71; text-align: center;">
                        <p style="margin:0; color:#7f8c8d; font-size:13px; font-weight:bold;">⏱️ Беглость ({emoji_speed} {rate:.1f} сил/сек)</p>
                        <p style="margin:5px 0 0 0; font-size: 24px; font-weight: bold; color: #27ae60;">{result['fluidity_score']:.0f} <span style="font-size:14px; color:#95a5a6;">/ 100</span></p>
                    </div>
                """, unsafe_allow_html=True)
                
            st.write("")
            
            score = result["score"]
            if score >= 80:
                st.balloons()
                st.markdown(f"<h3 style='color: #27ae60; margin:0;'>🎯 Общая оценка: {score:.1f} / 100 (Отлично!)</h3>", unsafe_allow_html=True)
            elif score >= 50:
                st.markdown(f"<h3 style='color: #f39c12; margin:0;'>🏃‍♂️ Общая оценка: {score:.1f} / 100 (Хорошее начало)</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='color: #c0392b; margin:0;'>💪 Общая оценка: {score:.1f} / 100 (Нужно потренироваться)</h3>", unsafe_allow_html=True)
                
            st.progress(max(0.0, min(1.0, score / 100)))
            st.write(f"💬 **Совет тренера:** {feedback}")
            
        except Exception as e:
            st.error(f"Ошибка анализа: {e}")
