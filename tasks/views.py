from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.exceptions import PermissionDenied

from tasks.forms import SignUpForm
from tasks.models import Project, ProjectAccess, Task
from tasks.serializers import ProjectSerializer, TaskSerializer


def index(request: HttpRequest):
    """
    Renders homepage
    """
    return render(request, 'tasks/index.html')


def login(request: HttpRequest):
    """
    Renders login page
    """
    return render(request, 'tasks/login.html')


class UserSignUpForm(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('tasks:login')
    template_name = "tasks/signup.html"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)

        if self.request.method in ('POST', 'PUT'):
            username = kwargs['data'].get('username', '')
            kwargs['data'] = self.request.POST.copy()
            kwargs['data'].update({'email': username})
        return kwargs


class UserLoginView(LoginView):
    template_name = "tasks/login.html"
    extra_context = {'next': reverse_lazy('tasks:home')}
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    template_name = "tasks/logout.html"
    extra_context = {'logged_out': True}


class ProjectList(ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.project_set.all()

    def perform_create(self, serializer: ProjectSerializer):
        if (serializer.is_valid()):
            project: Project = serializer.save()
            ProjectAccess.objects.create(
                project=project,
                user=self.request.user,
                membership_level=ProjectAccess.MembershipLevel.OWNER)
        return project


class TaskList(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.task_set.all()

    def perform_create(self, serializer: TaskSerializer):
        if serializer.is_valid():
            project: Project = serializer.validated_data.get('project')
            try:
                project = self.request.user.project_set.get(pk=project.pk)
                task: Task = serializer.save(owner=self.request.user)
            except Project.DoesNotExist:
                raise PermissionDenied(
                    "Could not find that project or you don't have permission")
            except ...:
                raise PermissionDenied("Unknown error")
        return task
