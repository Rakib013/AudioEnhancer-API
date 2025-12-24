import os
import tempfile
import subprocess
import torch
from df.enhance import enhance, init_df, load_audio, save_audio
from df.io import resample

# Initialize model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, df, _ = init_df(model_base_dir=None, config_allow_defaults=True)
model = model.to(device=device).eval()


def convert_to_wav(input_path: str) -> str:
    """Convert audio file to standard WAV format (48kHz, mono, PCM 16-bit)"""
    # Always re-encode to ensure compatibility (especially for browser-recorded audio)
    output_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    
    try:
        # Try ffmpeg first with additional verbosity to catch format issues
        result = subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '48000',
            '-ac', '1',
            output_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            # Log ffmpeg error for debugging
            if result.stderr:
                print(f"FFmpeg stderr: {result.stderr}")
    except Exception as e:
        print(f"FFmpeg exception: {e}")
    
    # Fallback to pydub
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(48000).set_channels(1)
        audio.export(output_path, format='wav')
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
    except Exception as e:
        print(f"Pydub failed: {e}")
        # Clean up failed output file
        if os.path.exists(output_path):
            os.remove(output_path)
        raise Exception(f"Could not convert audio file: {e}")


def reduce_noise(audio_path: str) -> str:
    """
    Reduce noise from audio file using DeepFilterNet.
    
    Args:
        audio_path (str): Path to input audio file (mp3, wav, ogg, etc.)
        
    Returns:
        str: Path to denoised output WAV file
    """
    # Convert to standard WAV format if needed
    wav_path = convert_to_wav(audio_path)
    should_cleanup = wav_path != audio_path
    
    try:
        # Load audio at 48kHz (DeepFilterNet native sample rate)
        sr = 48000
        sample, meta = load_audio(wav_path, sr)
        
        # Handle multi-channel audio - convert to mono
        if sample.dim() > 1 and sample.shape[0] > 1:
            sample = sample.mean(dim=0, keepdim=True)
        
        # Apply noise reduction using DeepFilterNet
        enhanced = enhance(model, df, sample)
        
        # Apply fade-in to avoid clicks at the beginning
        fade_duration = int(sr * 0.15)
        fade_in = torch.linspace(0.0, 1.0, fade_duration).unsqueeze(0)
        enhanced[:, :fade_duration] = enhanced[:, :fade_duration] * fade_in
        
        # Resample back to original sample rate if needed
        if meta.sample_rate != sr:
            enhanced = resample(enhanced, sr, meta.sample_rate)
            sr = meta.sample_rate
        
        # Save enhanced audio
        output_path = tempfile.NamedTemporaryFile(suffix="_denoised.wav", delete=False).name
        save_audio(output_path, enhanced, sr)
        
        return output_path
        
    finally:
        # Clean up temporary converted file
        if should_cleanup and os.path.exists(wav_path):
            os.remove(wav_path)
