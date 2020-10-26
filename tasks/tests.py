import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse_lazy
from tasks.models import ProjectAccess


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
