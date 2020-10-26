import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse_lazy


class TaskTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="jane_doe@email.com",
                                        email="jane_doe@email.com",
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

    def create_task(self,
                    user=None,
                    title="Test Task Title",
                    description="Test Task Desctiption",
                    project_id=1) -> HttpResponse:
        # Login
        if (user is not None):
            self.client.force_login(self.user)

        # Create Task
        response = self.client.post(
            reverse_lazy('tasks:tasks'),
            {
                'title': title,
                'description': description,
                'project': project_id
            },
            content_type="application/json",
        )

        # Return response
        return response

    def test_user_get_tasks(self):
        """
        Only authenticated users can have tasks
        """
        # Login and get tasks
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('tasks:tasks'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_get_tasks(self):
        """
        Anonymous users should not have tasks
        """
        # Get tasks without logging in
        response = self.client.get(reverse_lazy('tasks:tasks'))
        self.assertEqual(response.status_code, 403)

    def test_user_create_task(self):
        """
        A user can create a task
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())
        # Create task for that project
        task_response = self.create_task(user=self.user,
                                         project_id=project['id'])

        self.assertEqual(task_response.status_code, 201)

    def test_anonymous_create_task(self):
        """
        Anonymous users should not be able to create a task for a project
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())
        self.client.logout()

        # Try to create a task
        task_response = self.create_task(project_id=project['id'])

        self.assertEqual(task_response.status_code, 403)

    def test_user_put_task(self):
        """
        User should be able to update the task
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())

        # Create a task
        task_response = self.create_task(project_id=project['id'])
        task = json.loads(task_response.content.decode())

        # Update the task
        task_update_response = self.client.put(reverse_lazy(
            'tasks:task', kwargs={'pk': task['id']}), {
                'title': 'Updated Task Title',
                'description': 'Updated Task Description',
                'project': project['id']
            },
                                               content_type='application/json')

        self.assertEqual(task_update_response.status_code, 200)

    def test_anonymous_put_task(self):
        """
        Anonymous users cannot update tasks
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())

        # Create a task
        task_response = self.create_task(project_id=project['id'])
        task = json.loads(task_response.content.decode())

        # Logout
        self.client.logout()

        # Update the task
        task_update_response = self.client.put(reverse_lazy(
            'tasks:task', kwargs={'pk': task['id']}), {
                'title': 'Updated Task Title',
                'description': 'Updated Task Description',
                'project': project['id']
            },
                                               content_type='application/json')

        self.assertEqual(task_update_response.status_code, 403)

    def test_user_patch_task(self):
        """
        User can patch a task
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())

        # Create a task
        task_response = self.create_task(project_id=project['id'])
        task = json.loads(task_response.content.decode())

        # Update the task
        task_update_response = self.client.patch(
            reverse_lazy('tasks:task', kwargs={'pk': task['id']}), {
                'title': 'Updated Task Title',
                'description': 'Updated Task Description',
            },
            content_type='application/json')

        self.assertEqual(task_update_response.status_code, 200)

    def test_anonymous_patch_task(self):
        """
        Anonymous user cannot patch a task
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())

        # Create a task
        task_response = self.create_task(project_id=project['id'])
        task = json.loads(task_response.content.decode())

        # Logout
        self.client.logout()

        # Update the task
        task_update_response = self.client.patch(
            reverse_lazy('tasks:task', kwargs={'pk': task['id']}), {
                'title': 'Updated Task Title',
                'description': 'Updated Task Description',
            },
            content_type='application/json')

        self.assertEqual(task_update_response.status_code, 403)

    def test_user_delete_task(self):
        """
        User can delete a task
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())

        # Create a task
        task_response = self.create_task(project_id=project['id'])
        task = json.loads(task_response.content.decode())

        # Delete the task
        task_delete_response = self.client.delete(
            reverse_lazy('tasks:task', kwargs={'pk': task['id']}))

        self.assertEqual(task_delete_response.status_code, 204)

    def test_anonymous_delete_task(self):
        """
        User can delete a task
        """
        # Create project
        project_response = self.create_project(user=self.user)
        project = json.loads(project_response.content.decode())

        # Create a task
        task_response = self.create_task(project_id=project['id'])
        task = json.loads(task_response.content.decode())

        # Logout
        self.client.logout()

        # Delete the task
        task_delete_response = self.client.delete(
            reverse_lazy('tasks:task', kwargs={'pk': task['id']}))

        self.assertEqual(task_delete_response.status_code, 403)
