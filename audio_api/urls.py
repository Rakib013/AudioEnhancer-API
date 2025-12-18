from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AudioProcessingViewSet, home_view, 
                   noise_reducer_view, volume_booster_view)

router = DefaultRouter()
router.register(r'audio', AudioProcessingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', home_view, name='home'),
    path('noise-reducer/', noise_reducer_view, name='noise_reducer'),
    path('volume-booster/', volume_booster_view, name='volume_booster'),
]
