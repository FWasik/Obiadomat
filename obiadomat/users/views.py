from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.messages.views import SuccessMessageMixin


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    template_name = "register.html"
    success_url = reverse_lazy("users:login")
    success_message = "You successfully created an account!"
