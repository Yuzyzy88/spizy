from rest_framework.serializers import ModelSerializer, ReadOnlyField

from tasks.models import Project, Task


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description']


class TaskSerializer(ModelSerializer):
    owner = ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'owner']
