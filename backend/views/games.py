from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from api.models import Game


class Index(LoginRequiredMixin, ListView):
    model = Game
    template_name = "backend/games/index.html"
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().order_by('-date_started')


class Show(LoginRequiredMixin, DetailView):
    model = Game
    template_name = "backend/games/show.html"


class Delete(LoginRequiredMixin, DeleteView):
    model = Game
    success_url = reverse_lazy('games')
    template_name = "backend/games/delete.html"
