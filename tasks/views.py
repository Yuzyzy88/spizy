from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic import CreateView
from .forms import SignUpForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView


def index(request: HttpRequest):
    """
    Renders homepage
    """
    return render(request, 'tasks/index.html')


def login(request: HttpRequest):
    """
    Renders login page
    """
    return render(request, 'tasks/login.html')


class UserSignUpForm(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('tasks:login')
    template_name = "tasks/signup.html"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)

        if self.request.method in ('POST', 'PUT'):
            username = kwargs['data'].get('username', '')
            kwargs['data'] = self.request.POST.copy()
            kwargs['data'].update({'email': username})
        return kwargs


class UserLoginView(LoginView):
    template_name = "tasks/login.html"
    extra_context = {'next': reverse_lazy('tasks:home')}
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    template_name = "tasks/logout.html"
    extra_context = {'logged_out': True}
