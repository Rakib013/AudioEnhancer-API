import matplotlib
matplotlib.use('Agg')

import math
import os
import tempfile
import subprocess
from typing import Optional, Tuple
import numpy as np
import torch
from torch import Tensor
import matplotlib.pyplot as plt
from PIL import Image
from df import config
from df.enhance import enhance, init_df, load_audio, save_audio
from df.io import resample

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, df, _ = init_df(model_base_dir=None, config_allow_defaults=True)
model = model.to(device=device).eval()

NOISES = {
    "None": None,
    "Kitchen": "samples/dkitchen.wav",
    "Living Room": "samples/dliving.wav",
    "River": "samples/nriver.wav",
    "Cafe": "samples/scafe.wav",
}

def convert_to_wav(input_path: str) -> str:
    """Convert audio file to WAV format if needed"""
    if input_path.lower().endswith('.wav'):
        return input_path
    
    output_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
    
    try:
        # Try ffmpeg first
        result = subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '48000',
            '-ac', '1',
            output_path
        ], capture_output=True, stderr=subprocess.DEVNULL)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
    except Exception as e:
        print(f"FFmpeg failed: {e}")
    
    # Fallback to pydub
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='wav')
        return output_path
    except Exception as e:
        print(f"Pydub failed: {e}")
        raise Exception(f"Could not convert audio file: {e}")

def mix_at_snr(clean, noise, snr, eps=1e-10):
    clean = torch.as_tensor(clean).mean(0, keepdim=True)
    noise = torch.as_tensor(noise).mean(0, keepdim=True)
    if noise.shape[1] < clean.shape[1]:
        noise = noise.repeat((1, int(math.ceil(clean.shape[1] / noise.shape[1]))))
    max_start = int(noise.shape[1] - clean.shape[1])
    start = torch.randint(0, max_start, ()).item() if max_start > 0 else 0
    noise = noise[:, start : start + clean.shape[1]]
    E_speech = torch.mean(clean.pow(2)) + eps
    E_noise = torch.mean(noise.pow(2))
    K = torch.sqrt((E_noise / E_speech) * 10 ** (snr / 10) + eps)
    noise = noise / K
    mixture = clean + noise
    assert torch.isfinite(mixture).all()
    max_m = mixture.abs().max()
    if max_m > 1:
        clean, noise, mixture = clean / max_m, noise / max_m, mixture / max_m
    return clean, noise, mixture

def process_audio(audio_path: str, noise_type: str = "None", snr: int = 10, max_duration: int = 60 * 60 * 60):
    # Convert to WAV if needed
    # print(f"Processing audio: {audio_path}")
    wav_path = convert_to_wav(audio_path)
    should_cleanup = wav_path != audio_path
    # print(f"Converted to: {wav_path}")
    
    try:
        sr = config("sr", 48000, int, section="df")
        sample, meta = load_audio(wav_path, sr)
        
        max_len = max_duration * sr
        if sample.shape[-1] > max_len:
            start = torch.randint(0, sample.shape[-1] - max_len, ()).item()
            sample = sample[..., start : start + max_len]
        
        if sample.dim() > 1 and sample.shape[0] > 1:
            sample = sample.mean(dim=0, keepdim=True)
        
        noise_fn = NOISES.get(noise_type)
        if noise_fn is not None and os.path.exists(noise_fn):
            noise, _ = load_audio(noise_fn, sr)
            _, _, sample = mix_at_snr(sample, noise, snr)
        
        enhanced = enhance(model, df, sample)
        
        lim = torch.linspace(0.0, 1.0, int(sr * 0.15)).unsqueeze(0)
        lim = torch.cat((lim, torch.ones(1, enhanced.shape[1] - lim.shape[1])), dim=1)
        enhanced = enhanced * lim
        
        if meta.sample_rate != sr:
            enhanced = resample(enhanced, sr, meta.sample_rate)
            sample = resample(sample, sr, meta.sample_rate)
            sr = meta.sample_rate
        
        noisy_wav = tempfile.NamedTemporaryFile(suffix="_noisy.wav", delete=False).name
        save_audio(noisy_wav, sample, sr)
        
        enhanced_wav = tempfile.NamedTemporaryFile(suffix="_enhanced.wav", delete=False).name
        save_audio(enhanced_wav, enhanced, sr)
        
        
        return noisy_wav, enhanced_wav
        
    finally:
        # Cleanup converted file
        if should_cleanup and os.path.exists(wav_path):
            os.remove(wav_path)
