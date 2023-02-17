from datetime import date

from rest_framework import serializers

from users.models import CustomUser
from users.serializers import UserSerializer

from .models import Comment
from .models import Note
from .models import NoteVersion


class CommentSerializer(serializers.ModelSerializer):
    commenter = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ['note', 'created_at', 'commenter']


class VersionHistorySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = NoteVersion
        fields = "__all__"
        read_only_fields = ['note', 'created_at', 'author']


class NoteSerializer(serializers.ModelSerializer):
    emails = serializers.ListField(child=serializers.EmailField(), required=False)
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    versions = VersionHistorySerializer(many=True, read_only=True)
    shared_with = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = "__all__"
        read_only_fields = ('created_at', 'modified_at', 'author')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "text" in validated_data and validated_data["text"] != instance.text:
            NoteVersion.objects.create(
                note=instance,
                content=instance.text,
                author=self.context['request'].user,
            )
        instance = super().update(instance, validated_data)
        return instance

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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')

        if request and 'pk' not in request.parser_context.get('kwargs', {}):

            if instance.comments.exists():
                ret['comments'] = CommentSerializer(instance.comments.last()).data
            else:
                ret.pop('comments')
            ret.pop('versions')
            ret.pop('shared_with')
        else:
            user = request.user
            shared_with = instance.shared_with.all()
            if user == instance.author or user in shared_with:
                ret['comments'] = CommentSerializer(instance.comments.order_by('-created_at'), many=True).data
                ret['versions'] = VersionHistorySerializer(instance.versions.order_by('-created_at'), many=True).data
                ret['shared_with'] = UserSerializer(instance.shared_with, many=True).data
            else:
                ret.pop('comments')
                ret.pop('versions')
                ret.pop('shared_with')
        return ret
