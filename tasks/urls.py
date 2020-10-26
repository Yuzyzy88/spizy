from django.urls import path
from tasks import views

# Namespace URL paths
app_name = "tasks"

urlpatterns = [
    path('', views.index, name="home"),
    path('signup', views.UserSignUpForm.as_view(), name="signup"),
    path('login', views.UserLoginView.as_view(), name="login"),
    path('logout', views.UserLogoutView.as_view(), name="logout"),
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
