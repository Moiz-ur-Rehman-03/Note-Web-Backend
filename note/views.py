from django.db.models import Q

from rest_framework.viewsets import ModelViewSet

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        return Note.objects.filter(Q(text__icontains=query) & Q(user=self.request.user))
