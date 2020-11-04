import io
from json.decoder import JSONDecodeError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.middleware import csrf
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.exceptions import (ParseError, PermissionDenied,
                                       ValidationError)
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from tasks.forms import SignUpForm
from tasks.models import Project, ProjectAccess, Task
from tasks.permissions import (IsTaskPartOfUserProject, IsUserOwnerOfProject,
                               IsUserPartOfProject)
from tasks.serializers import (ProjectAccessSerializer, ProjectSerializer,
                               SignUpFormSerializer, TaskSerializer,
                               UserSerializer)


def csrfview(request: HttpRequest):
    """
    Returns a CSRF token for use
    """
    return JsonResponse({'token': csrf.get_token(request)})


def UserLogin(request: HttpRequest):
    """
    Logs a user in via JSON request
    """
    try:
        # Try to parse the data as JSON
        stream = io.BytesIO(request.body)
        data = JSONParser().parse(stream)

        # Serialize the user data
        serializer = UserSerializer(data=data)

        # Will raise exception if data is invalid
        serializer.is_valid(raise_exception=True)

        # Check if the data is valid and try logging in
        form = AuthenticationForm(request=request,
                                  data=serializer.validated_data)

    except JSONDecodeError:
        return HttpResponseBadRequest()
    except BaseException:
        return HttpResponseBadRequest()

    if form.is_valid():
        user: User = authenticate(request=request,
                                  username=form.cleaned_data['username'],
                                  password=form.cleaned_data['password'])
        login(request, user)
        return JsonResponse({
            'status': True,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    else:
        return JsonResponse(data={"detail": "Incorrect username or password"},
                            status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def UserLogout(request: Request):
    logout(request)
    return JsonResponse({'status': True})


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def check_login(request: Request):
    """
    Checks if user is logged in
    """
    if (request.user.is_authenticated):
        return Response({
            'status': True,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })
    else:
        raise PermissionDenied('Please log in')


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
def UserSignUp(request: Request):
    """
    Signup User
    """
    # Serialize the data
    serializer = SignUpFormSerializer(data=request.data)

    # Verify Serialized Data
    serializer.is_valid(raise_exception=True)

    # Check with the form
    form = SignUpForm(data=serializer.validated_data)

    if form.is_valid():
        user: User = form.save(commit=True)
        return JsonResponse(
            data={
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            })
    else:
        raise ParseError(detail=form.errors)


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
        user_access = queryset.filter(user=self.request.user).get(
            project=project)

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
