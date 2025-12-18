from rest_framework import serializers
from .models import AudioProcessing

class AudioProcessingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioProcessing
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'noisy_audio', 'processed_audio', 
                           'noisy_spectrogram', 'enhanced_spectrogram']

class NoiseReductionSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    noise_type = serializers.ChoiceField(
        choices=['None', 'Kitchen', 'Living Room', 'River', 'Cafe'],
        default='None'
    )
    snr = serializers.ChoiceField(choices=['-5', '0', '10', '20'], default='10')

class VolumeBoostSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    mode = serializers.ChoiceField(
        choices=['0', '1', '2'],
        default='0',
        help_text='0: Mild, 1: Moderate, 2: Aggressive'
    )
