from django.contrib import admin

from .models import Comment
from .models import Note
from .models import NoteVersion

# Register your models here.
admin.site.register(Note)
admin.site.register(Comment)
admin.site.register(NoteVersion)
