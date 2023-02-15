from django.conf import settings
from django.db import models


class Note(models.Model):
    text = models.CharField(max_length=255, default="")
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="author", on_delete=models.CASCADE)
    archived_at = models.DateField(null=True, blank=True)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, default="")

    def __str__(self):
        return self.text
