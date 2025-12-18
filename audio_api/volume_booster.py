import matplotlib
matplotlib.use('Agg')

import tempfile
import torch
from voicefixer import VoiceFixer
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Initialize VoiceFixer model
voicefixer = VoiceFixer()

def spec_im_simple(audio_path: str) -> Image:
    """Generate spectrogram image from audio file"""
    import librosa
    import librosa.display
    
    y, sr = librosa.load(audio_path)
    
    # Create spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    
    figure = plt.figure(figsize=(15, 4))
    figure.set_tight_layout(True)
    
    ax = figure.add_subplot(111)
    img = librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', ax=ax, cmap='inferno')
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    
    figure.canvas.draw()
    buf = figure.canvas.buffer_rgba()
    w, h = figure.canvas.get_width_height()
    img = Image.frombuffer("RGBA", (w, h), buf, "raw", "RGBA", 0, 1)
    plt.close(figure)
    return img.convert("RGB")

def boost_volume(audio_path: str, mode: int = 0):
    """
    Boost audio volume using VoiceFixer
    
    Args:
        audio_path: Path to input audio file
        mode: 0 for mild enhancement, 1 for aggressive enhancement, 2 for very aggressive
    
    Returns:
        Tuple of (output_path, original_spectrogram, enhanced_spectrogram)
    """
    output_path = tempfile.NamedTemporaryFile(suffix="_boosted.wav", delete=False).name
    
    # Restore audio using VoiceFixer
    voicefixer.restore(
        input=audio_path,
        output=output_path,
        cuda=torch.cuda.is_available(),
        mode=mode
    )
    
    # Generate spectrograms
    original_spec = spec_im_simple(audio_path)
    enhanced_spec = spec_im_simple(output_path)
    
    return output_path, original_spec, enhanced_spec
