from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser, User
from django.urls import reverse_lazy


class ProjectTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="jane_doe",
                                        email="jane_doe@email.com",
                                        password="secret")
        self.client = Client()

    def test_user_project_create(self):
        """
        Creates project only for authenticated user
        """
        self.client.force_login(self.user)
        response = self.client.post(
            reverse_lazy('tasks:projects'),
            {
                "title": "Test Title",
                "description": "Test Description"
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

    def test_anonymous_project_create(self):
        """
        Anonymous users cannot create projects
        """
        response = self.client.post(
            reverse_lazy('tasks:projects'),
            {
                "title": "Test Title",
                "description": "Test Description"
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
