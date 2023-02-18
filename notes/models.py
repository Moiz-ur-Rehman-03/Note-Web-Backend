from django.conf import settings
from django.db import models


class Note(models.Model):
    text = models.CharField(max_length=255, default="")
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="author", on_delete=models.CASCADE, default=1)
    archived_at = models.DateField(null=True, blank=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, default="")

    def __str__(self):
        return self.text


class Comment(models.Model):
    note = models.ForeignKey('notes.Note', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="commenter", on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"Node id: {self.note.id} - Comment by {self.commenter.id} {self.commenter.email}"


class NoteVersion(models.Model):
    note = models.ForeignKey('notes.Note', on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='note_versions', default=1)

    def __str__(self):
        return f"Note id: {self.note.id} - Version number:{self.id} - Version by {self.author.id} - Version content:{self.content}"
