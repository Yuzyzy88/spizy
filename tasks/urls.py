from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# Namespace URL paths
app_name = "tasks"

urlpatterns = [
    path('', views.index, name="home"),
    path('signup', views.UserSignUpForm.as_view(), name="signup"),
    path('login', views.UserLoginView.as_view(), name="login"),
    path('logout', views.UserLogoutView.as_view(), name="logout"),
]
