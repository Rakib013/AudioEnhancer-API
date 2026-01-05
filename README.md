# AudioEnhancer-API

A Django-based REST API and web application for audio processing using AI models. Features noise reduction with DeepFilterNet2 and volume enhancement with VoiceFixer.

## Features

- **Noise Reduction**: Remove background noise from audio using DeepFilterNet2
- **Volume Boost**: Enhance and boost audio volume using VoiceFixer
- **Web Interface**: Upload audio files or record directly in the browser
- **REST API**: Full API endpoints for programmatic access
- **Spectrogram Visualization**: Visual comparison of noisy vs enhanced audio

## Tech Stack

- Python 3.10+
- Django & Django REST Framework
- PyTorch & DeepFilterNet2
- VoiceFixer
- Librosa, SoundFile
- FFmpeg for audio conversion

## Installation

### Prerequisites

- Python 3.10 or higher
- FFmpeg

**Install FFmpeg:**

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/AudioEnhancer-API.git
cd AudioEnhancer-API
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

## Usage

### Web Interface

- **Home**: `http://localhost:8000/`
- **Noise Reducer**: `http://localhost:8000/noise-reducer/`
- **Volume Booster**: `http://localhost:8000/volume-booster/`

### API Endpoints

#### Noise Reduction

```http
POST /api/audio/denoise/
```

**Request Body (form-data):**
- `audio_file`: Audio file to process
- `noise_type`: Optional. One of `None`, `Kitchen`, `Living Room`, `River`, `Cafe`
- `snr`: Optional. Signal-to-noise ratio (`-5`, `0`, `10`, `20`)

**Response:**
```json
{
  "id": "uuid",
  "original_audio": "/media/audio/original/file.wav",
  "processed_audio": "/media/audio/processed/enhanced.wav",
  "noisy_spectrogram": "/media/spectrograms/noisy/spec.png",
  "enhanced_spectrogram": "/media/spectrograms/enhanced/spec.png",
  "processing_type": "noise_reduction",
  "created_at": "2026-01-05T10:30:00Z"
}
```

#### Volume Boost

```http
POST /api/audio/boost/
```

**Request Body (form-data):**
- `audio_file`: Audio file to boost
- `mode`: Enhancement mode (`0` = mild, `1` = moderate, `2` = aggressive)

## Project Structure

```
AudioEnhancer-API/
├── audio_processor/          # Django project settings
├── audio_api/               # Main application
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── audio_processor.py   # DeepFilterNet2 processing
│   ├── noise_reducer.py     # Noise reduction logic
│   ├── volume_booster.py    # VoiceFixer processing
│   └── templates/           # HTML templates
├── media/                   # Uploaded and processed files
├── manage.py
└── requirements.txt
```

## Models

### DeepFilterNet2
State-of-the-art speech enhancement model that removes background noise while preserving speech quality.

### VoiceFixer
AI-powered audio restoration tool that enhances volume and overall audio quality.

## Development

The project uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
