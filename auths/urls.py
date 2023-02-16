from django.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import LoginView
from .views import RegisterView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
