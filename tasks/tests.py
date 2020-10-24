from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from django.urls import reverse_lazy
import json


class ProjectTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="jane_doe",
                                        email="jane_doe@email.com",
                                        password="secret")
        self.client = Client()

    def create_project(self,
                       user=None,
                       title="Test Title",
                       description="Test Description"):
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
                "title": "Test Title",
                "description": "Test Description"
            },
            content_type="application/json",
        )

        # Return Response
        return response

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

    def test_delete_project(self):
        """
        Test project creation and deletion
        """
        # Login and Create Project
        self.client.force_login(self.user)
        create_response = self.create_project(self.user)
        project_detail = json.loads(create_response.content.decode())

        # Delete Project
        delete_response = self.client.delete(
            reverse_lazy('tasks:project',
                         kwargs={'pk': int(project_detail['id'])}))

        self.assertEqual(delete_response.status_code, 204)

    def test_update_project(self):
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
