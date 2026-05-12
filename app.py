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
}

.stButton > button[kind="primary"] {
    background-color: #2c2c2c;
    color: white;
    border: none;
    border-radius: 8px;
}

.stButton > button[kind="secondary"] {
    background-color: white;
    color: #2c2c2c;
    border: 2px solid #2c2c2c;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return load_dataset(DATA_PATH)


def save_uploaded_file(uploaded_file) -> str:
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    suffix = Path(uploaded_file.name).suffix
    filename = f"user_audio_{int(time.time())}{suffix}"
    save_path = upload_dir / filename
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(save_path)


df, is_real_dataset = load_data()

with st.sidebar:
    st.title("K-Read Coach")
    st.caption("Korean Read-Aloud Practice")

    if not is_real_dataset:
        st.warning("Using mock data — place k_read_coach_dataset.csv in data/")

    categories = get_categories(df)
    selected_category = st.selectbox("TOPIC", categories)

    sentences_df = get_sentences_by_category(df, selected_category)
    if sentences_df.empty:
        st.error("No sentences found for this category.")
        st.stop()
    selected_sentence = st.selectbox("SENTENCE", sentences_df["sentence"].tolist())

st.header("Practice Session")

row = sentences_df[sentences_df["sentence"] == selected_sentence].iloc[0]
target_sentence = row["sentence"]

st.markdown(f'<div class="sentence-card">{html.escape(target_sentence)}</div>', unsafe_allow_html=True)

st.write(f"**English:** {row['english_translation']}")

st.subheader("Reference Audio")
reference_audio_path = (Path(CLIPS_DIR) / row["path"]).resolve()
clips_base = Path(CLIPS_DIR).resolve()
if not str(reference_audio_path).startswith(str(clips_base)):
    st.error("Invalid audio path detected.")
    st.stop()
if is_real_dataset and reference_audio_path.exists():
    st.audio(str(reference_audio_path))
elif is_real_dataset:
    st.warning(f"Reference audio not found: {reference_audio_path}")
else:
    st.warning("Reference audio unavailable in mock mode.")

st.subheader("Your Reading")
uploaded_file = st.file_uploader("Upload your audio", type=["wav", "mp3", "m4a"])

col1, col2 = st.columns(2)
with col1:
    analyze = st.button("Analyze", type="primary", use_container_width=True)
with col2:
    retry = st.button("Retry", type="secondary", use_container_width=True)

if retry:
    st.rerun()

if analyze:
    if uploaded_file is None:
        st.warning("Please upload your reading audio first.")
    else:
        try:
            with st.spinner("Analyzing your reading..."):
                path = save_uploaded_file(uploaded_file)
                try:
                    recognized = transcribe_audio(path)
                    if not recognized:
                        st.warning("Could not recognize speech. Please check your audio and try again.")
                        st.stop()
                    result = compare_texts(target_sentence, recognized)
                    feedback = generate_feedback(result["score"])
                finally:
                    Path(path).unlink(missing_ok=True)

            st.subheader("Results")
            st.write(f"**Recognized Text:** {result['recognized']}")
            st.write("**Score:**")
            st.progress(max(0.0, min(1.0, result["score"] / 100)))
            st.write(f"{result['score']:.1f} / 100")
            st.write(f"**Feedback:** {feedback}")
        except Exception as e:
            st.error(f"Analysis failed: {e}")