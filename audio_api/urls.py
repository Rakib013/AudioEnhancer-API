from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AudioProcessingViewSet, home_view, 
                   noise_reducer_view, volume_booster_view, signup_view, login_view, logout_view, profile_view)

router = DefaultRouter()
router.register(r'audio', AudioProcessingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', home_view, name='home'),
    path('noise-reducer/', noise_reducer_view, name='noise_reducer'),
    path('volume-booster/', volume_booster_view, name='volume_booster'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]
