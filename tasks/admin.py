from django.contrib import admin
from tasks.models import Project, ProjectAccess, Task

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(ProjectAccess)
