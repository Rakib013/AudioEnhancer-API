***

# Audio Processor

Audio Processor is a Django-based web and API service for processing audio files.  
It provides:

- Noise reduction using **DeepFilterNet2**
- Volume boosting and enhancement using **VoiceFixer**
- A web UI (upload or record audio)
- REST APIs for programmatic access

***

## Features

- **Noise Reducer**
  - Denoise speech audio with DeepFilterNet2
  - Optionally mix in synthetic background noise (Kitchen, Cafe, River, etc.)
- **Volume Booster**
  - Enhance and boost volume using VoiceFixer
  - Multiple enhancement modes (mild → aggressive)
- **Web Interface**
  - Upload audio files
  - Record audio in the browser (MediaRecorder API)
  - Visual comparison: noisy/original vs processed spectrograms
- **REST API**
  - `POST /api/audio/denoise/` – noise reduction
  - `POST /api/audio/boost/` – volume boost

***

## Tech Stack

- Python 3.x  
- Django, Django REST Framework  
- PyTorch, DeepFilterNet2, VoiceFixer  
- `librosa`, `soundfile`, `ffmpeg` for audio I/O  
- HTML + JavaScript (MediaRecorder) for browser recording

***

## Project Structure

```text
audio_processor/
├── audio_processor/          # Django project (settings, root URLs)
├── audio_api/                # Main app (API, views, templates)
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── audio_processor.py    # DeepFilterNet2 logic
│   ├── volume_booster.py     # VoiceFixer logic
│   └── templates/audio_api/
│       ├── base.html
│       ├── home.html
│       ├── noise_reducer.html
│       ├── noise_result.html
│       ├── volume_booster.html
│       └── boost_result.html
├── manage.py
└── requirements.txt
```

***

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Install **ffmpeg** (needed for WebM/OGG → WAV conversion):

```bash
# macOS (Homebrew)
brew install ffmpeg
```

### 3. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Run the development server

```bash
python manage.py runserver
```

Open the app at:  
`http://localhost:8000/`

***

## Usage

### Web UI

- **Home:** `http://localhost:8000/`
- **Noise reducer:** `http://localhost:8000/noise-reducer/`
  - Record audio or upload an audio file
  - Choose noise type and SNR
  - Listen to noisy vs enhanced audio and view their spectrograms
- **Volume booster:** `http://localhost:8000/volume-booster/`
  - Upload an audio file
  - Select enhancement mode (0 = mild, 1 = moderate, 2 = aggressive)
  - Compare original vs boosted audio and spectrograms

### REST API

#### 1. Noise Reduction

**Endpoint**

```http
POST /api/audio/denoise/
```

**Body (form-data)**

- `audio_file` (File, required): input audio file  
- `noise_type` (Text, optional): one of `None`, `Kitchen`, `Living Room`, `River`, `Cafe`  
- `snr` (Text, optional): one of `-5`, `0`, `10`, `20`  

**Example (Postman)**

- Body → `form-data`
  - `audio_file` → type: `File` → choose your file
  - `noise_type` → `None`
  - `snr` → `10`

**Example response**

```json
{
  "id": "UUID",
  "original_audio": "/media/audio/original/yourfile.wav",
  "processed_audio": "/media/audio/processed/enhanced_UUID.wav",
  "noisy_audio": "/media/audio/noisy/noisy_UUID.wav",
  "noisy_spectrogram": "/media/spectrograms/noisy/noisy_spec_UUID.png",
  "enhanced_spectrogram": "/media/spectrograms/enhanced/enh_spec_UUID.png",
  "noise_type": "None",
  "snr": 10,
  "processing_type": "noise_reduction",
  "created_at": "2025-12-19T00:00:00Z"
}
```

#### 2. Volume Boost

**Endpoint**

```http
POST /api/audio/boost/
```

**Body (form-data)**

- `audio_file` (File, required): input audio file  
- `mode` (Text, optional): `0`, `1`, or `2`  
  - `0` = mild  
  - `1` = moderate  
  - `2` = aggressive  

**Example response**

```json
{
  "id": "UUID",
  "original_audio": "/media/audio/original/yourfile.wav",
  "processed_audio": "/media/audio/processed/boosted_UUID.wav",
  "noisy_spectrogram": "/media/spectrograms/noisy/orig_spec_UUID.png",
  "enhanced_spectrogram": "/media/spectrograms/enhanced/boosted_spec_UUID.png",
  "processing_type": "volume_boost",
  "created_at": "2025-12-19T00:00:00Z"
}
```

***

## Environment Variables (optional)

If you use environment variables (e.g., `.env`):

- `DJANGO_DEBUG` – `True`/`False`  
- `DJANGO_SECRET_KEY` – secret key for Django  
- `DJANGO_ALLOWED_HOSTS` – comma-separated host list  

Document any others you add.

***

## Development Notes

- For large audio files, processing time and memory usage will increase.
- Models (DeepFilterNet2, VoiceFixer) may download weights on first run.
- For production, configure:
  - Proper static/media hosting
  - HTTPS
  - A real database (PostgreSQL, etc.)