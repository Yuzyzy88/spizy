import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse_lazy
from tasks.models import ProjectAccess


class ProjectAccessTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_jane = User.objects.create(username="jane_doe@email.com",
                                             email="jane_doe@email.com",
                                             password="secret")
        self.user_bob = User.objects.create(username="bob_doe@email.com",
                                            email="bob_doe@email.com",
                                            password="secret")
        self.user_steve = User.objects.create(username="steve_doe@email.com",
                                              email="steve_doe@email.com",
                                              password="secret")
        self.client = Client()

    def create_project(self,
                       user=None,
                       title="Test Title",
                       description="Test Description") -> HttpResponse:
        """
        Utility function to create project and return the JSON data
        """
        # Login
        if (user is not None):
            self.client.force_login(user)

        # Create Project
        response = self.client.post(
            reverse_lazy('tasks:projects'),
            {
                "title": title,
                "description": description,
            },
            content_type="application/json",
        )

        # Return Response
        return response

    def test_user_get_accesslist(self):
        """
        User can have an access list
        """
        # Login
        self.client.force_login(self.user_jane)
        # Get user access list
        access_response = self.client.get(
            reverse_lazy('tasks:projectaccesslist'))

        self.assertEqual(access_response.status_code, 200)

    def test_anonymous_get_accesslist(self):
        """
        Anonymous user cannot have an access list
        """
        # Get user access list without logging in
        access_response = self.client.get(
            reverse_lazy('tasks:projectaccesslist'))

        self.assertEqual(access_response.status_code, 403)

    def test_owner_create_access(self):
        """
        Owner of the project can create access
        """
        # Create project
        project_response = self.create_project(self.user_jane)
        project = json.loads(project_response.content.decode())

        # Create Access
        access_response = self.client.post(
            reverse_lazy('tasks:projectaccesslist'), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })

        self.assertEqual(access_response.status_code, 201)

    def test_member_create_access(self):
        """
        A member of the project cannot create access
        """
        # Create project
        project_response = self.create_project(self.user_jane)
        project = json.loads(project_response.content.decode())

        # Create Access
        self.client.post(
            reverse_lazy('tasks:projectaccesslist'), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })

        # Logout and login as the member
        self.client.logout()
        self.client.force_login(self.user_bob)

        # Try creating the access for another user
        access_response = self.client.post(
            reverse_lazy('tasks:projectaccesslist'), {
                'user': self.user_steve.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })

        self.assertEqual(access_response.status_code, 403)

    def test_anonymous_create_access(self):
        """
        Anonymous user cannot create access
        """
        # Create project
        project_response = self.create_project(self.user_jane)
        project = json.loads(project_response.content.decode())

        # Logout
        self.client.logout()

        # Create Access
        access_response = self.client.post(
            reverse_lazy('tasks:projectaccesslist'), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })

        self.assertEqual(access_response.status_code, 403)

    def test_owner_update_access(self):
        """
        Owner of a project can update access
        """
        # Create project
        project_response = self.create_project(self.user_jane)
        project = json.loads(project_response.content.decode())

        # Create Access
        access_response = self.client.post(
            reverse_lazy('tasks:projectaccesslist'), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })
        access = json.loads(access_response.content.decode())
        # Update the access (via PUT)
        put_response = self.client.put(
            reverse_lazy('tasks:projectaccess', kwargs={'pk': access['id']}), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.OWNER
            },
            content_type='application/json')
        self.assertEqual(put_response.status_code, 200)

        # Update the access (via PATCH)
        patch_response = self.client.patch(
            reverse_lazy('tasks:projectaccess', kwargs={'pk': access['id']}), {
                'user': self.user_bob.username,
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            },
            content_type='application/json')
        self.assertEqual(patch_response.status_code, 200)

    def test_member_update_access(self):
        """
        Members of a project cannot update access
        """
        # Create project
        project_response = self.create_project(self.user_jane)
        project = json.loads(project_response.content.decode())

        # Create Access
        access_response = self.client.post(
            reverse_lazy('tasks:projectaccesslist'), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })
        access = json.loads(access_response.content.decode())

        # Logout and login with member level permissions
        self.client.logout()
        self.client.force_login(self.user_bob)

        # Try to update the access (via PUT)
        put_response = self.client.put(
            reverse_lazy('tasks:projectaccess', kwargs={'pk': access['id']}), {
                'user': self.user_bob.username,
                'project': project['id'],
                'membership_level': ProjectAccess.MembershipLevel.OWNER
            })
        self.assertEqual(put_response.status_code, 403)

        # Try to update the access (via PATCH)
        patch_response = self.client.patch(
            reverse_lazy('tasks:projectaccess', kwargs={'pk': access['id']}), {
                'user': self.user_bob.username,
                'membership_level': ProjectAccess.MembershipLevel.MEMBER
            })
        self.assertEqual(patch_response.status_code, 403)
