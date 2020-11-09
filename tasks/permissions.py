from django.db.models import Q
from django.http.request import HttpRequest
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from tasks.models import Project, ProjectAccess, Task


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

        return False


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
                # Get All User Projects
                user_projects = request.user.project_set.all()

                # For every project the user is part of,
                # get all the project members and their access level
                filters = Q()
                for project in user_projects:
                    filters |= Q(project=project)

                # Try to get the task
                Task.objects.filter(filters).get(pk=obj.pk)

                # If got task means, user is part of it
                return True

        except Task.DoesNotExist:
            raise PermissionDenied("You don't have permission to do that")
        except Exception:
            raise PermissionDenied("Unknown error")

        return False


class IsUserOwnerOfProject(BasePermission):
    """
    Object-level permission to check if the user is owner of the project
    """
    def has_object_permission(self, request: HttpRequest, view,
                              obj: ProjectAccess):
        try:
            if request.user.is_anonymous:
                raise NotAuthenticated('You need to login first')
            elif request.method in SAFE_METHODS:
                return True
            elif request.method not in SAFE_METHODS:
                ProjectAccess.objects.get(
                    user=request.user,
                    project=obj.project,
                    membership_level=ProjectAccess.MembershipLevel.OWNER)
                return True
        except ProjectAccess.DoesNotExist:
            raise PermissionDenied("You don't have permission to do that")
        except Exception:
            raise PermissionDenied("Unknown error")

        return False
