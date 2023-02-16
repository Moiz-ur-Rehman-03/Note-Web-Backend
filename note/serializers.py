from datetime import date

from rest_framework import serializers

from auths.models import CustomUser

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    emails = serializers.ListField(child=serializers.EmailField(), required=False)

    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ('created_at', 'modified_at', 'author')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def validate_archived_at(self, value):
        try:
            if value < date.today():
                raise serializers.ValidationError("Cannot archive note with date in the past.")
        except (TypeError, ValueError):
            raise serializers.ValidationError("Invalid date format.")
        return value

    def validate_emails(self, emails):
        instance = self.instance
        emails_exist = {}
        for email in emails:
            user = CustomUser.objects.filter(email=email).first()
            if not instance.shared_with.filter(id=user.id).exists() and user.id != self.context.get('request').user.id:
                emails_exist[email] = user.id

        return emails_exist
