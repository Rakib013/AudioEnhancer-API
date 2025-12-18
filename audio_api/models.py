from django.db import models
import uuid

class AudioProcessing(models.Model):
    PROCESSING_TYPES = [
        ('noise_reduction', 'Noise Reduction'),
        ('volume_boost', 'Volume Boost'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_audio = models.FileField(upload_to='audio/original/')
    processed_audio = models.FileField(upload_to='audio/processed/', null=True, blank=True)
    
    # For noise reduction
    noisy_audio = models.FileField(upload_to='audio/noisy/', null=True, blank=True)
    noisy_spectrogram = models.ImageField(upload_to='spectrograms/noisy/', null=True, blank=True)
    enhanced_spectrogram = models.ImageField(upload_to='spectrograms/enhanced/', null=True, blank=True)
    noise_type = models.CharField(max_length=50, default='None', blank=True)
    snr = models.IntegerField(default=10, null=True, blank=True)
    
    # Processing metadata
    processing_type = models.CharField(max_length=20, choices=PROCESSING_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
