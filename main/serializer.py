from rest_framework import serializers
from .models import User, Project

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'member_name',
            'member_nickname',
            'member_auth',
        )
        model = User