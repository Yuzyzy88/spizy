from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticated

from tasks.forms import SignUpForm
from tasks.models import Project, ProjectAccess, Task
from tasks.permissions import (IsTaskPartOfUserProject, IsUserOwnerOfProject,
                               IsUserPartOfProject)
from tasks.serializers import (ProjectAccessSerializer, ProjectSerializer,
                               TaskSerializer)


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
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsUserPartOfProject]

    def get_queryset(self):
        return self.request.user.project_set.all()

    def perform_create(self, serializer: ProjectSerializer):
        project: Project = serializer.save()
        ProjectAccess.objects.create(
            project=project,
            user=self.request.user,
            membership_level=ProjectAccess.MembershipLevel.OWNER)

        return project


class ProjectDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsUserPartOfProject]

    def get_queryset(self):
        return self.request.user.project_set.all()

    def get_object(self):
        # Query the object
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        # Filter the object
        filter_kwargs = {}
        filter_kwargs[self.lookup_field] = self.kwargs[self.lookup_field]

        # Check permissions before return
        obj = get_object_or_404(
            queryset,
            **filter_kwargs,
        )
        self.check_object_permissions(self.request, obj)
        return obj


class TaskList(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.task_set.all()

    def perform_create(self, serializer: TaskSerializer):
        # Get the project
        project: Project = serializer.validated_data.get('project')
        try:
            # Try to get project the user is part of
            self.request.user.project_set.get(pk=project.pk)
            # Save the task
            task: Task = serializer.save(owner=self.request.user)
        except Project.DoesNotExist:
            raise PermissionDenied(
                "Could not find that project or you don't have permission")
        except ...:
            raise PermissionDenied("Unknown error")

        return task


class TaskDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskPartOfUserProject]

    def get_queryset(self):
        return self.request.user.task_set.all()

    def get_object(self):
        # Query the object
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        # Filter the object
        filter_kwargs = {}
        filter_kwargs[self.lookup_field] = self.kwargs[self.lookup_field]

        # Check the permission before return
        obj: Task = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj


class ProjectAccessList(ListCreateAPIView):
    """
    Project Access List & Create API Endpoint
    """

    serializer_class = ProjectAccessSerializer
    permission_classes = [IsAuthenticated & IsUserOwnerOfProject]

    def get_queryset(self):
        # Get All User Projects
        user_projects = self.request.user.project_set.all()

        # For every project the user is part of,
        # get all the project members and their access level
        filters = Q()
        for project in user_projects:
            filters |= Q(project=project)

        return ProjectAccess.objects.filter(filters)

    def perform_create(self, serializer: ProjectAccessSerializer):
        # Queryset
        queryset = self.get_queryset()
        # Get the project
        project: Project = serializer.validated_data.get('project', None)
        # Get the user that should be given access
        user: User = get_object_or_404(
            User,
            username=serializer.validated_data.get('user').get('username'))
        # Check if the user is the OWNER of the project;
        # Owners of the project may add access
        user_access = queryset.filter(user=self.request.user).get(project=project)

        # Check if the user is the owner
        self.check_object_permissions(self.request, user_access)

        access = serializer.save(user=user)

        return access


class ProjectAccessDetail(RetrieveUpdateDestroyAPIView):
    """
    Project Access Retreive, Update, Destroy API Endpoint
    """
    serializer_class = ProjectAccessSerializer
    permission_classes = [IsAuthenticated & IsUserOwnerOfProject]

    def get_queryset(self):
        # Get All User Projects
        user_projects = self.request.user.project_set.all()

        # For every project the user is part of,
        # get all the project members and their access level
        filters = Q()
        for project in user_projects:
            filters |= Q(project=project)

        return ProjectAccess.objects.filter(filters)

    def get_object(self):
        # Get the queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Get the object
        filter_kwarg = {self.lookup_field: self.kwargs[self.lookup_field]}
        obj = get_object_or_404(queryset, **filter_kwarg)
        # Check permissions
        self.check_object_permissions(self.request, obj)

        return obj

    def perform_update(self, serializer: ProjectAccessSerializer):
        """
        Perform Update on Project Access
        """
        # Get the user that should be given access
        user: User = get_object_or_404(
            User,
            username=serializer.validated_data.get('user').get('username'))
        serializer.save(user=user)