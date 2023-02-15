from django.urls import include
from django.urls import path

from rest_framework import routers

from .views import NoteViewSet

router = routers.DefaultRouter()
router.register(r'', NoteViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
