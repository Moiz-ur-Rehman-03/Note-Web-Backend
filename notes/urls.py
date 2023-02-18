from django.urls import include
from django.urls import path

from rest_framework import routers

from .views import CommentGetAndCreateAPIView
from .views import NoteViewSet
from .views import VersionGetAPIView
from .views import VersionPutAPIView

router = routers.DefaultRouter()
router.register(r'', NoteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:note_id>/comments/', CommentGetAndCreateAPIView.as_view(), name='comment-list-create'),
    path('<int:note_id>/versions/', VersionGetAPIView.as_view(), name='get-versions'),
    path('<int:note_id>/versions/<int:version_id>/', VersionPutAPIView.as_view(), name='put-version'),
]
