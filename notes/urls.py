from django.urls import include
from django.urls import path

from rest_framework import routers

from .views import CommentCreateAPIView
from .views import NoteViewSet
from .views import RevertNoteAPIView

router = routers.DefaultRouter()
router.register(r'', NoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:note_id>/comments/', CommentCreateAPIView.as_view(), name='comment-list-create'),
    path('<int:note_id>/original-version/', RevertNoteAPIView.as_view(), name='note-original-version'),
]
