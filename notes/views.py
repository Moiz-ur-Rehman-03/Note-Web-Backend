from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from utils.send_email import send_email

from .custom_filters import ArchivedAtFilterBackend
from .models import Comment
from .models import Note
from .models import NoteVersion
from .permissions import IsAuthor
from .permissions import IsSharedWith
from .serializers import CommentSerializer
from .serializers import NoteSerializer
from .serializers import VersionHistorySerializer


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor | IsSharedWith]
    queryset = Note.objects.all()
    filter_backends = [ArchivedAtFilterBackend]

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        return Note.objects.filter(
            (Q(author=self.request.user) | Q(shared_with__in=[self.request.user])) &
            Q(text__icontains=query),
        ).distinct()

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


class CommentGetAndCreateAPIView(generics.CreateAPIView, generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        note_id = self.kwargs.get('note_id')
        user = self.request.user
        return Comment.objects.filter(
            Q(note=note_id) &
            (Q(note__author=user) | Q(note__shared_with__in=[user])),
        ).order_by('-created_at').distinct()

    def create(self, request, *args, **kwargs):
        note_id = kwargs['note_id']

        note = get_object_or_404(Note, id=note_id)
        if note.author == request.user or request.user in note.shared_with.all():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(note=note, commenter=request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"error": "You are not authorized to create a comment on this note."}, status=status.HTTP_403_FORBIDDEN)


class VersionGetAPIView(generics.ListAPIView):
    serializer_class = VersionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        note_id = self.kwargs.get('note_id')
        user = self.request.user
        return NoteVersion.objects.filter(
            Q(note=note_id) &
            (Q(note__author=user) | Q(note__shared_with__in=[user])),
        ).order_by('-created_at').distinct()


class VersionPutAPIView(generics.UpdateAPIView):
    serializer_class = VersionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, note_id, version_id):
        try:
            note = Note.objects.get(id=note_id)
            version_note = NoteVersion.objects.filter(Q(note=note) & Q(id=version_id)).order_by('created_at')

            note.text = version_note[0].content
            note.save()
            NoteVersion.objects.create(
                note=note,
                content=note.text,
                author=note.author,
            )

            serializer = NoteSerializer(note, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Note.DoesNotExist:
            return Response({"detail": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
