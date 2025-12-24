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
    return output_path
