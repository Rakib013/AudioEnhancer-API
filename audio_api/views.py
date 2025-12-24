import os
from django.shortcuts import render
from django.core.files import File
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AudioProcessing
from .serializers import (AudioProcessingSerializer, NoiseReductionSerializer, VolumeBoostSerializer)
from .audio_processor import process_audio, NOISES
from .volume_booster import boost_volume

class AudioProcessingViewSet(viewsets.ModelViewSet):
    queryset = AudioProcessing.objects.all()
    serializer_class = AudioProcessingSerializer
    
    @action(detail=False, methods=['post'])
    def denoise(self, request):
        """Noise reduction endpoint"""
        serializer = NoiseReductionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = serializer.validated_data['audio_file']
        noise_type = serializer.validated_data['noise_type']
        snr = int(serializer.validated_data['snr'])
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            noise_type=noise_type,
            snr=snr,
            processing_type='noise_reduction'
        )
        
        try:
            noisy_path, enhanced_path = process_audio(
                audio_obj.original_audio.path,
                noise_type,
                snr
            )
            
            with open(noisy_path, 'rb') as f:
                audio_obj.noisy_audio.save(f'noisy_{audio_obj.id}.wav', File(f), save=False)
            
            with open(enhanced_path, 'rb') as f:
                audio_obj.processed_audio.save(f'enhanced_{audio_obj.id}.wav', File(f), save=False)

            audio_obj.save()
            
            os.remove(noisy_path)
            os.remove(enhanced_path)
            
            response_serializer = AudioProcessingSerializer(audio_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            audio_obj.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def boost(self, request):
        """Volume boost endpoint"""
        serializer = VolumeBoostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = serializer.validated_data['audio_file']
        mode = int(serializer.validated_data['mode'])
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            processing_type='volume_boost'
        )
        
        try:
            boosted_path = boost_volume(
                audio_obj.original_audio.path,
                mode
            )
            
            with open(boosted_path, 'rb') as f:
                audio_obj.processed_audio.save(f'boosted_{audio_obj.id}.wav', File(f), save=False)
            
            audio_obj.save()
            
            os.remove(boosted_path)
            
            response_serializer = AudioProcessingSerializer(audio_obj)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            audio_obj.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Web Template Views
def home_view(request):
    return render(request, 'audio_api/home.html')

def noise_reducer_view(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        noise_type = request.POST.get('noise_type', 'None')
        snr = int(request.POST.get('snr', '10'))
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            noise_type=noise_type,
            snr=snr,
            processing_type='noise_reduction'
        )
        
        try:
            noisy_path, enhanced_path = process_audio(
                audio_obj.original_audio.path,
                noise_type,
                snr
            )
            
            with open(noisy_path, 'rb') as f:
                audio_obj.noisy_audio.save(f'noisy_{audio_obj.id}.wav', File(f), save=False)
            
            with open(enhanced_path, 'rb') as f:
                audio_obj.processed_audio.save(f'enhanced_{audio_obj.id}.wav', File(f), save=False)
            
            audio_obj.save()
            
            os.remove(noisy_path)
            os.remove(enhanced_path)
            
            return render(request, 'audio_api/noise_result.html', {'audio': audio_obj})
            
        except Exception as e:
            audio_obj.delete()
            return render(request, 'audio_api/noise_reducer.html', {
                'error': str(e),
                'noises': NOISES.keys()
            })
    
    return render(request, 'audio_api/noise_reducer.html', {'noises': NOISES.keys()})

def volume_booster_view(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        mode = int(request.POST.get('mode', '0'))
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            processing_type='volume_boost'
        )
        
        try:
            boosted_path = boost_volume(
                audio_obj.original_audio.path,
                mode
            )
            
            with open(boosted_path, 'rb') as f:
                audio_obj.processed_audio.save(f'boosted_{audio_obj.id}.wav', File(f), save=False)
            
            audio_obj.save()
            
            os.remove(boosted_path)
            
            return render(request, 'audio_api/boost_result.html', {'audio': audio_obj})
            
        except Exception as e:
            audio_obj.delete()
            return render(request, 'audio_api/volume_booster.html', {'error': str(e)})
    
    return render(request, 'audio_api/volume_booster.html')
