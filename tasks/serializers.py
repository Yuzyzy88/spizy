from rest_framework.serializers import (EmailField, ModelSerializer,
                                        ReadOnlyField)

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
        fields = ['id', 'title', 'description', 'project', 'owner']


class ProjectAccessSerializer(ModelSerializer):
    """
    Serializer for ProjecAccess Model
    """
    user = EmailField(source='user.username')

    class Meta:
        model = ProjectAccess
        fields = ['id', 'project', 'user', 'membership_level']
