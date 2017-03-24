from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from backend.models import Endpoint


class Index(LoginRequiredMixin, ListView):
    model = Endpoint
    template_name = "backend/endpoints/index.html"

    def get_queryset(self):
        if "q" in self.request.GET:
            q = self.request.GET['q']
            if len(q) > 0:
                return Endpoint.objects.filter(name__icontains=q)

        return super().get_queryset()


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
