from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from api.models import ConfigurationKey
from backend.forms import ConfigurationKeyForm


class Index(LoginRequiredMixin, ListView):
    model = ConfigurationKey
    template_name = "backend/config/index.html"


class Create(LoginRequiredMixin, CreateView):
    model = ConfigurationKey
    success_url = reverse_lazy('config')
    form_class = ConfigurationKeyForm
    template_name = "backend/config/form.html"


class Update(LoginRequiredMixin, UpdateView):
    model = ConfigurationKey
    success_url = reverse_lazy('config')
    form_class = ConfigurationKeyForm
    template_name = "backend/config/form.html"

    def get_initial(self):
        ctx = super().get_initial()
        ctx['value'] = self.object.raw_value

        return ctx


class Delete(LoginRequiredMixin, DeleteView):
    model = ConfigurationKey
    success_url = reverse_lazy('config')
    template_name = "backend/config/delete.html"
