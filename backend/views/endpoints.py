from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from backend.models import Endpoint


class Index(LoginRequiredMixin, ListView):
    model = Endpoint
    template_name = "backend/endpoints/index.html"


class Create(LoginRequiredMixin, CreateView):
    model = Endpoint
    success_url = reverse_lazy('endpoints')
    fields = ['name', 'number']
    template_name = "backend/endpoints/form.html"


class Update(LoginRequiredMixin, UpdateView):
    model = Endpoint
    success_url = reverse_lazy('endpoints')
    fields = ['name', 'number']
    template_name = "backend/endpoints/form.html"


class Delete(LoginRequiredMixin, DeleteView):
    model = Endpoint
    success_url = reverse_lazy('endpoints')
    template_name = "backend/endpoints/delete.html"
