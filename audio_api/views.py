import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files import File
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AudioProcessing
from .serializers import (AudioProcessingSerializer, NoiseReductionSerializer, VolumeBoostSerializer)
from .noise_reducer import reduce_noise
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
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            user=request.user if request.user.is_authenticated else None,
            processing_type='noise_reduction'
        )
        
        try:
            enhanced_path = reduce_noise(audio_obj.original_audio.path)
            
            with open(enhanced_path, 'rb') as f:
                audio_obj.processed_audio.save(f'enhanced_{audio_obj.id}.wav', File(f), save=False)

            audio_obj.save()
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
            user=request.user if request.user.is_authenticated else None,
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
        
        if not audio_file:
            return render(request, 'audio_api/noise_reducer.html', {
                'error': 'No audio file provided'
            }, status=400)
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            user=request.user if request.user.is_authenticated else None,
            processing_type='noise_reduction'
        )
        
        try:
            print(f"Processing audio file: {audio_obj.original_audio.path}")
            enhanced_path = reduce_noise(audio_obj.original_audio.path)
            
            if not enhanced_path or not os.path.exists(enhanced_path):
                raise Exception("Audio processing returned no file")
            
            with open(enhanced_path, 'rb') as f:
                audio_obj.processed_audio.save(f'enhanced_{audio_obj.id}.wav', File(f), save=False)
            
            audio_obj.save()
            os.remove(enhanced_path)
            
            # Return the result page with 200 status
            response = render(request, 'audio_api/noise_result.html', {'audio': audio_obj})
            return response
            
        except Exception as e:
            print(f"Error during audio processing: {str(e)}")
            import traceback
            traceback.print_exc()
            audio_obj.delete()
            return render(request, 'audio_api/noise_reducer.html', {
                'error': str(e)
            }, status=400)
    
    return render(request, 'audio_api/noise_reducer.html')

def volume_booster_view(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        mode = int(request.POST.get('mode', '0'))
        
        audio_obj = AudioProcessing.objects.create(
            original_audio=audio_file,
            user=request.user if request.user.is_authenticated else None,
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


# Authentication Views
def signup_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            return render(request, 'audio_api/signup.html', {'error': 'Passwords do not match'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'audio_api/signup.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'audio_api/signup.html', {'error': 'Email already exists'})
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('home')
        except Exception as e:
            return render(request, 'audio_api/signup.html', {'error': str(e)})
    
    return render(request, 'audio_api/signup.html')


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'audio_api/login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'audio_api/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('home')


def profile_view(request):
    """User profile - shows their uploaded files"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_files = AudioProcessing.objects.filter(user=request.user)
    noise_reduction_count = user_files.filter(processing_type='noise_reduction').count()
    volume_boost_count = user_files.filter(processing_type='volume_boost').count()
    
    return render(request, 'audio_api/profile.html', {
        'audio_files': user_files,
        'noise_reduction_count': noise_reduction_count,
        'volume_boost_count': volume_boost_count,
    })