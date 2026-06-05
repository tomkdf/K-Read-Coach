# K-Read Coach 🇰🇷 

An interactive Web application designed specifically for Russian native speakers to practice and master Korean read-aloud pronunciation. Powered by Streamlit and automated Speech Recognition (ASR).

---

## 🚀 Features

- **Targeted Practice Modules:** Sentences curated from everyday real-life topics (Shopping, Transportation, Dining, School, etc.).
- **Automatic Audio Analysis:** Leverages advanced AI transcription models (`faster-whisper`) to analyze phonetic output.
- **Instant Pronunciation Scoring:** Utilizes Levenshtein distance calculations at the Jamo (Korean alphabet component) level to give hyper-accurate phonetic feedback scores out of 100.
- **Russian Translation Support:** Custom automated translations using KSS (Korean Speech Script) raw datasets converted to Russian.
- **In-Browser Recording:** Integrated native HTML5 JavaScript microphone audio recording capabilities seamlessly injected into the Streamlit ecosystem.

---

## 🛠️ Installation & Setup

Follow these steps to set up and run the application on any local machine (Linux, macOS, or Windows).

### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd K-Read-Coach
```

### 2. Create and Activate a Virtual Environment

It is highly recommended to isolate the project requirements using a Python virtual environment (venv).

On Linux / macOS:
```bash
  python3 -m venv venv
  source venv/bin/activate
```
On Windows (PowerShell):
```bash
  python -m venv venv
  .\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install all core application and engine dependencies dynamically using the curated requirements manifest:

```bash
pip install -r requirements.txt
```
### 4. Run the Application
Start the local development server:

```bash
streamlit run app.py
```
Open your browser and navigate to http://localhost:8501 to begin practicing!

### 📂 Project Architecture

```bash
K-Read-Coach/
├── app.py # Core application controller and Streamlit user interface layout.
├── dataset_cleaning.py # Text parsing pipeline translating English KSS files into a Russian schema.
├── extract_audio.py # Audio synchronizer sorting and validating target audio references.
├── requirements.txt # Production dependencies and library pins.
├── README.md # Project documentation.
├── data/
│   ├── k_read_coach_dataset.csv # Cleansed and structured dataset (Korean/Russian mapping).
│   └── clips/ # Target reference audio assets (.wav format).
└── modules/
    ├── asr_interface.py # Interface executing Whisper AI speech-to-text transcriptions.
    ├── comparison.py # Phonetic analyzer performing Levenshtein algorithms on extracted Jamos.
    ├── data_loader.py # Local database ingestion utility handling system memory cache.
    └── feedback.py # Logic matrix returning interactive instructional critique.
```
## ⚙️ Data Engineering & Customization

If you want to modify, alter topics, or generate a brand new set of sentences using the KSS transcript baseline datasets:

Place your raw transcript.txt file at the root directory.

Open dataset_cleaning.py and tweak the num_sentences parameter or adjust the targeted keywords array.

Re-run the data processing engine:

```bash
python dataset_cleaning.py
```
Sync and match your file paths with the target reference waveforms:

```bash
python extract_audio.py
```
---

## 🔒 Browser Security Warning (Microphone Context)

Due to modern web browser security constraints regarding **Secure Contexts**, media hardware like the microphone will **ONLY** work when accessing the application locally:

* `http://localhost:8501`

If you attempt to access the application via a local network IP address (e.g., `http://172.22...`) from another device like a mobile phone or a second laptop, the browser will strictly block microphone access. For development and testing, **always run and use the application on your local machine.**