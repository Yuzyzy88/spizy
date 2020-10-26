from django.urls import path
from tasks import views

# Namespace URL paths
app_name = "tasks"

urlpatterns = [
    path('csrftoken', views.csrfview, name='csrfview'),
    # User Views
    path('signup', views.UserSignUp, name="signup"),
    path('login', views.UserLogin, name="login"),
    path('check-login', views.check_login, name="checklogin"),
    path('logout', views.UserLogout, name="logout"),
    # API View
    path('projects', views.ProjectList.as_view(), name="projects"),
    path('project/<int:pk>', views.ProjectDetail.as_view(), name="project"),
    path('tasks', views.TaskList.as_view(), name="tasks"),
    path('task/<int:pk>', views.TaskDetail.as_view(), name="task"),
    path('project-access',
         views.ProjectAccessList.as_view(),
         name="projectaccesslist"),
    path('project-access/<int:pk>',
         views.ProjectAccessDetail.as_view(),
         name="projectaccess"),
]
