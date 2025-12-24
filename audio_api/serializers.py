from rest_framework import serializers
from .models import AudioProcessing

class AudioProcessingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioProcessing
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'noisy_audio', 'processed_audio']

class NoiseReductionSerializer(serializers.Serializer):
    audio_file = serializers.FileField()

class VolumeBoostSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    mode = serializers.ChoiceField(
        choices=['0', '1', '2'],
        default='0',
        help_text='0: Mild, 1: Moderate, 2: Aggressive'
    )