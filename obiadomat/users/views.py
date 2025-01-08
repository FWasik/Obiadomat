from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import CustomUserUpdateForm
from django.shortcuts import render, redirect
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


class CustomPasswordResetView(SuccessMessageMixin, auth_views.PasswordResetView):
    template_name = "password_reset_form.html"
    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "emails/password_reset_subject.txt"
    success_url = reverse_lazy("users:login")
    success_message = "A password reset email was sent!"


class CustomPasswordResetConfirmView(
    SuccessMessageMixin, auth_views.PasswordResetConfirmView
):
    template_name = "password_reset_confirm.html"
    success_url = reverse_lazy("users:login")
    success_message = "A password was reset!"


@login_required
def update_user_info_and_password(request):
    user_form = CustomUserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        if "user_info_submit" in request.POST:
            user_form = CustomUserUpdateForm(request.POST, instance=request.user)

            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Your profile information has been updated!")

        elif "password_change_submit" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, "Your password has been successfully updated!"
                )

    return render(
        request,
        "update_user_info_and_password.html",
        {"user_form": user_form, "password_form": password_form},
    )
