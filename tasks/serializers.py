from django.contrib.auth.models import User
from rest_framework.serializers import (CharField, EmailField, ModelSerializer,
                                        ReadOnlyField, Serializer)

from tasks.models import Project, ProjectAccess, Task


class ProjectSerializer(ModelSerializer):
    """
    Serializer for Project Model
    """
    class Meta:
        model = Project
        fields = ['id', 'title', 'description']


class TaskSerializer(ModelSerializer):
    """
    Serializer for Task Model
    """

    owner = ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'owner', 'progress',
            'due_date'
        ]


class ProjectAccessSerializer(ModelSerializer):
    """
    Serializer for ProjecAccess Model
    """
    user = EmailField(source='user.username')

    class Meta:
        model = ProjectAccess
        fields = ['id', 'project', 'user', 'membership_level']


class UserSerializer(ModelSerializer):
    """
    Serializer for User Model
    """
    username = EmailField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password']


class SignUpFormSerializer(Serializer):
    """
    Serializer for Sign Up Form
    """
    username = EmailField(max_length=128)
    password1 = CharField(max_length=128, min_length=6, allow_blank=False)
    password2 = CharField(max_length=128, min_length=6, allow_blank=False)
    first_name = CharField(max_length=128, min_length=1, allow_blank=False)
    last_name = CharField(max_length=128, min_length=1, allow_blank=False)
