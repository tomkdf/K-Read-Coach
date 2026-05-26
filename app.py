import html
import time
from pathlib import Path
import streamlit as st
from modules.data_loader import load_dataset, get_categories, get_sentences_by_category
from modules.asr_interface import transcribe_audio
from modules.comparison import compare_texts
from modules.feedback import generate_feedback
import streamlit.components.v1 as components
import base64

DATA_PATH = "data/k_read_coach_dataset.csv"
CLIPS_DIR = "data/clips"

# --- THÈME GRAPHIQUE CUSTOM ---
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

/* Style de vos boutons manuels d'action */
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
st.write(f"**Russian:** {row['russian_translation']}")

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

# --- GESTION DE LA MÉMOIRE DE L'ENREGISTREMENT (SESSION STATE) ---
if "saved_audio_base64" not in st.session_state:
    st.session_state["saved_audio_base64"] = ""

# Intercepter l'audio qui arrive de l'URL (Query Parameters)
query_params = st.query_params
if "audio_data" in query_params:
    st.session_state["saved_audio_base64"] = query_params["audio_data"]
    st.query_params.clear() # On nettoie l'URL proprement

# 1. TON Enregistreur HTML/JS (Fait juste Start/Stop)
components.html("""
<div id="recorder-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif; margin: 10px 0;">
    <button id="record-btn" style="
        background-color: #2c2c2c;
        color: white;
        border: none;
        border-radius: 50%;
        width: 90px;
        height: 90px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        outline: none;
    ]">
        <svg id="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
    </button>
    <p id="status-text" style="color: #2c2c2c; font-weight: 600; font-size: 14px; margin-top: 16px; letter-spacing: 0.5px; text-transform: uppercase;">Tap to Record</p>
</div>

<script>
    const recordBtn = document.getElementById('record-btn');
    const statusText = document.getElementById('status-text');
    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];

    recordBtn.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await window.parent.navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => { audioChunks.push(event.data); };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64Data = reader.result.split(',')[1];
                        
                        // Envoi sécurisé via URL
                        const parentUrl = new URL(window.parent.location.href);
                        parentUrl.searchParams.set('audio_data', base64Data);
                        window.parent.history.replaceState({}, '', parentUrl.toString());
                        
                        window.parent.document.querySelector('.stApp').dispatchEvent(new Event('readystatechange'));
                        window.parent.location.reload();
                    };
                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start();
                isRecording = true;
                
                recordBtn.style.backgroundColor = '#e74c3c';
                recordBtn.style.transform = 'scale(1.1)';
                recordBtn.style.boxShadow = '0 0 20px rgba(231, 76, 60, 0.5)';
                statusText.innerText = 'Recording...';
                statusText.style.color = '#e74c3c';
            } catch (err) {
                statusText.innerText = 'Mic Blocked';
                console.error(err);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            
            recordBtn.style.backgroundColor = '#2c2c2c';
            recordBtn.style.transform = 'scale(1)';
            recordBtn.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
            statusText.innerText = 'Processing...';
            statusText.style.color = '#2c2c2c';
        }
    });
</script>
""", height=160)

# 2. Si un enregistrement existe, on affiche le lecteur de contrôle
audio_bytes = None
if st.session_state["saved_audio_base64"]:
    audio_bytes = base64.b64decode(st.session_state["saved_audio_base64"])
    st.audio(audio_bytes, format="audio/wav")

st.markdown("---")

# 3. LES DEUX BOUTONS ÉPURÉS
col1, col2 = st.columns(2)

with col1:
    analyze_clicked = st.button("✨ Analyze Voice", type="primary", use_container_width=True)

with col2:
    retry_clicked = st.button("🔄 Retry", type="secondary", use_container_width=True)

# Si l'utilisateur veut recommencer
if retry_clicked:
    st.session_state["saved_audio_base64"] = ""
    st.rerun()

# Si l'utilisateur clique sur Analyse
if analyze_clicked:
    if not audio_bytes:
        st.warning("Please record your voice first!")
    else:
        try:
            with st.spinner("✨ K-Read Coach is analyzing your pronunciation..."):
                upload_dir = Path("uploads")
                upload_dir.mkdir(exist_ok=True)
                path = str(upload_dir / f"user_audio_{int(time.time())}.wav")
                
                with open(path, "wb") as f:
                    f.write(audio_bytes)
                
                try:
                    recognized = transcribe_audio(path)
                    if not recognized:
                        st.warning("We couldn't quite hear you. Please try moving closer to the microphone!")
                        st.stop()
                    result = compare_texts(target_sentence, recognized)
                    feedback = generate_feedback(result["score"])
                finally:
                    Path(path).unlink(missing_ok=True)

            # --- AFFICHAGE PREMIUM DES RÉSULTATS ---
            st.success("🎉 Analysis complete!")
            st.subheader("📊 Performance Summary")
            
            st.markdown(f"""
                <div style="background-color: white; padding: 24px; border-radius: 12px; border: 1px solid #e8e0d8; margin-bottom: 20px;">
                    <p style="margin:0 0 8px 0; color:#7f8c8d; text-transform: uppercase; font-size:12px; font-weight:bold; letter-spacing:0.5px;">What the coach heard</p>
                    <p style="margin:0; font-size: 22px; font-weight: bold; color: #2c2c2c;">{result['recognized']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            score = result["score"]
            if score >= 80:
                st.balloons()
                st.markdown(f"<h3 style='color: #27ae60; margin:0;'>🎯 Score: {score:.1f} / 100 (Excellent!)</h3>", unsafe_allow_html=True)
            elif score >= 50:
                st.markdown(f"<h3 style='color: #f39c12; margin:0;'>🏃‍♂️ Score: {score:.1f} / 100 (Good Start)</h3>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h3 style='color: #c0392b; margin:0;'>💪 Score: {score:.1f} / 100 (Keep Practicing)</h3>", unsafe_allow_html=True)
                
            st.progress(max(0.0, min(1.0, score / 100)))
            st.write(f"💬 **Coach's Advice:** {feedback}")
            
        except Exception as e:
            st.error(f"Analysis failed: {e}")