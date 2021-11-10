from django.db.models import fields
from rest_framework import serializers
from .models import Comment, File, Member, Notification, Participant, Schedule, Todo, User, Project

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'password',
            'name',
            'email'
        )
        model = User

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
            'team',
            'description',
            'subject',
            'purpose',
            'progress_rate'
        )
        model = Project

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'project',
            'user',
            'leader',
            'contribution_rate'
        )
        model = Member

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'project',
            'invitee',
            'inviter',
            'invite_date'
        )
        model = Notification


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'project',
            'writer',
            'title',
            'description',
            'start_date',
            'end_date'
        )
        model = Schedule

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'project',
            'writer',
            'title',
            'description',
            'file_name',
            'file_url',
            'creat_at'
        )
        model = File

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'project',
            'writer',
            'title',
            'description',
            'state',
            'start_date',
            'end_date'
        )
        model = Todo


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'todo',
            'user'
        )
        model = Participant

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'todo',
            'writer',
            'content',
            'create_at'
        )
        model = Comment