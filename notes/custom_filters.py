from datetime import date

from rest_framework import filters


class ArchivedAtFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(archived_at__gte=date.today()) | queryset.filter(archived_at__isnull=True)
