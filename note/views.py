from datetime import date

from django.db.models import Q

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response

from utils.send_email import send_email

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        current_date = date.today()
        return Note.objects.filter(
            Q(text__icontains=query) &
            (Q(archived_at__gte=current_date) | Q(archived_at=None)),
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "emails" in serializer.validated_data.keys():
            emails = serializer.validated_data["emails"]

            for email, id in emails.items():
                instance.shared_with.add(id)

            send_email(
                subject="Shared a New Note",
                message='Hi ,\n I shared a new note with you.',
                emails=list(emails.keys()),
            )
        else:
            self.perform_update(serializer)

        return Response(serializer.validated_data)
