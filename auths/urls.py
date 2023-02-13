from django.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import UserLoginViewSet
from .views import UserRegistrationViewSet

router = DefaultRouter()
router.register('register', UserRegistrationViewSet, basename='register')
router.register('login', UserLoginViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
]
