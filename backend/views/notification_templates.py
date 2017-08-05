from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from api.models import NotificationTemplate
from backend.forms import NotificationTemplateForm


class Index(LoginRequiredMixin, ListView):
    model = NotificationTemplate
    template_name = "backend/notification_templates/index.html"
    paginate_by = 25

    # def get_queryset(self):
    #     qs = super(Index, self).get_queryset()
    #     start_time = self.request.GET.get('start', None)
    #     period = self.request.GET.get('period', None)
    #
    #     if start_time or period:
    #         if start_time is None:
    #             start_time = datetime.now()
    #         else:
    #             start_time = datetime.strptime(start_time, "%Y-%m-%d")
    #
    #         if period is None:
    #             period = timedelta(seconds=24 * 3600)
    #         else:
    #             period = timedelta(seconds=int(period))
    #
    #         end_time = start_time - period
    #
    #         print("Start Time", start_time)
    #         print("End Time", end_time)
    #         print("Period", period)
    #
    #         syncs = qs.objects.filter(when__gte=end_time, when__lte=start_time)
    #     else:
    #         print("All syncs ...")
    #         syncs = qs.all()
    #
    #     return syncs.order_by('-when')


class Create(LoginRequiredMixin, CreateView):
    model = NotificationTemplate
    form_class = NotificationTemplateForm
    template_name = "backend/notification_templates/form.html"
    success_url = reverse_lazy('notification_templates')


class Update(LoginRequiredMixin, UpdateView):
    model = NotificationTemplate
    form_class = NotificationTemplateForm
    template_name = "backend/notification_templates/form.html"
    success_url = reverse_lazy('notification_templates')


class Delete(LoginRequiredMixin, DeleteView):
    model = NotificationTemplate
    template_name = "backend/notification_templates/delete.html"
    success_url = reverse_lazy('notification_templates')

