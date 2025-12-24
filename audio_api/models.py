from django.db import models
from django.contrib.auth.models import User
import uuid

class AudioProcessing(models.Model):
    PROCESSING_TYPES = [
        ('noise_reduction', 'Noise Reduction'),
        ('volume_boost', 'Volume Boost'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Nullable for guest users
    original_audio = models.FileField(upload_to='audio/original/')
    processed_audio = models.FileField(upload_to='audio/processed/', null=True, blank=True)
    
    # Processing metadata
    processing_type = models.CharField(max_length=20, choices=PROCESSING_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']