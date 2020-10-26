import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse_lazy


class ProjectTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="jane_doe@email.com",
                                        email="jane_doe@email.com",
                                        password="secret")
        self.member = User.objects.create(username="jane_doe2@email.com",
                                          email="jane_doe2@email.com",
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
                "description": description
            },
            content_type="application/json",
        )

        # Return Response
        return response

    def test_user_get_project(self):
        """
        User is allowed to have projects
        """
        # Login and get projects
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('tasks:projects'))

        self.assertEqual(response.status_code, 200)

    def test_anonymous_get_project(self):
        """
        Anonymous user is not allowed to have projects
        """
        # Do not login and try to retreive projects
        response = self.client.get(reverse_lazy('tasks:projects'))
        self.assertEqual(response.status_code, 403)

    def test_user_create_project(self):
        """
        Creates project only for authenticated user
        """
        # Login and Create Project
        self.client.force_login(self.user)
        response = self.create_project(self.user)

        self.assertEqual(response.status_code, 201)

    def test_anonymous_create_project(self):
        """
        Anonymous users cannot create projects
        """
        # Create project without logging in
        response = self.create_project(None)

        self.assertEqual(response.status_code, 403)

    def test_user_delete_project(self):
        """
        Test project creation and deletion
        """
        # Login and Create Project
        self.client.force_login(self.user)
        create_response = self.create_project(self.user)
        project_detail = json.loads(create_response.content.decode())

        # Delete Project
        delete_response = self.client.delete(
            reverse_lazy('tasks:project', kwargs={'pk': project_detail['id']}))

        self.assertEqual(delete_response.status_code, 204)

    def test_anonymous_delete_project(self):
        """
        Anonymous users should not be able to delete a project
        """
        # Login and Create Project
        self.client.force_login(self.user)
        create_response = self.create_project(self.user)
        project_detail = json.loads(create_response.content.decode())
        self.client.logout()

        # Try deleting the project as an anonymous user
        delete_response = self.client.delete(
            reverse_lazy('tasks:project', kwargs={'pk': project_detail['id']}))

        self.assertEqual(delete_response.status_code, 403)

    def test_user_update_project(self):
        """
        Test project update
        """
        # Login and Create Project
        self.client.force_login(self.user)
        create_response = self.create_project(self.user)
        project_detail = json.loads(create_response.content.decode())

        # Update Project
        update_response = self.client.put(
            reverse_lazy('tasks:project',
                         kwargs={'pk': int(project_detail['id'])}),
            {
                "title": "Updated Title",
                "description": "Updated Title"
            },
            content_type="application/json",
        )

        # Check Status Code
        self.assertEqual(update_response.status_code, 200)

    def test_anonymous_update_project(self):
        """
        Test project update
        """
        # Login and Create Project and then logout
        self.client.force_login(self.user)
        create_response = self.create_project(self.user)
        project_detail = json.loads(create_response.content.decode())
        self.client.logout()

        # Update Project
        update_response = self.client.put(
            reverse_lazy('tasks:project',
                         kwargs={'pk': int(project_detail['id'])}),
            {
                "title": "Updated Title",
                "description": "Updated Title"
            },
            content_type="application/json",
        )

        # Check Status Code
        self.assertEqual(update_response.status_code, 403)
