from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class Project(models.Model):

    title = models.TextField()

    description = models.TextField()

    access = models.ManyToManyField(User,
                                    through='ProjectAccess',
                                    through_fields=('project', 'user'))

    class Meta:
        verbose_name = "project"
        verbose_name_plural = "projects"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tasks:project_detail", kwargs={"pk": self.pk})


class ProjectAccess(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class MembershipLevel(models.IntegerChoices):
        OWNER = 1
        MEMBER = 2

    membership_level = models.IntegerField(choices=MembershipLevel.choices)

    class Meta:
        verbose_name = "projectaccess"
        verbose_name_plural = "projectaccess"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projectaccess_detail", kwargs={"pk": self.pk})


class Task(models.Model):

    title = models.TextField()
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "task"
        verbose_name_plural = "tasks"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tasks:task_detail", kwargs={"pk": self.pk})