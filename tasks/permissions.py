from django.http.request import HttpRequest
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission

from tasks.models import Project, Task


class IsUserPartOfProject(BasePermission):
    """
    Object-level permission to check if the user is part of the project
    """
    def has_object_permission(self, request: HttpRequest, view, obj: Project):
        try:
            if request.user.is_anonymous:
                raise NotAuthenticated('You need to login first')
            else:
                request.user.project_set.get(pk=obj.pk)
                return True

        except Project.DoesNotExist:
            raise PermissionDenied("You don't have permission to do that")
        except Exception:
            raise PermissionDenied("Unknown error")


class IsTaskPartOfUserProject(BasePermission):
    """
    Object-level permission to check if the task is part of a project the user
    has access to.
    """
    def has_object_permission(self, request: HttpRequest, view, obj: Task):
        try:
            if request.user.is_anonymous:
                raise NotAuthenticated('You need to login first')
            else:
                request.user.task_set.get(pk=obj.pk)
                return True
        except Task.DoesNotExist:
            raise PermissionDenied("You don't have permission to do that")
        except Exception:
            raise PermissionDenied("Unknown error")
