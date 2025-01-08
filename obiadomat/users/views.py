from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    template_name = "register.html"
    success_url = reverse_lazy("users:login")
    success_message = "You successfully created an account!"


class LoginView(SuccessMessageMixin, auth_views.LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    template_name = "login.html"
    success_message = "You successfully logged in!"


class LogoutView(SuccessMessageMixin, LoginRequiredMixin, auth_views.LogoutView):
    success_message = "You successfully logged out!"

    def dispatch(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().dispatch(request, *args, **kwargs)
