from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView

from api.models import Notification
from backend.forms import NotificationForm


class Index(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "backend/notifications/index.html"
    paginate_by = 25

    def get_queryset(self):
        qs = super(Index, self).get_queryset()
        start_time = self.request.GET.get('start', None)
        period = self.request.GET.get('period', None)

        if start_time or period:
            if start_time is None:
                start_time = datetime.now()
            else:
                start_time = datetime.strptime(start_time, "%Y-%m-%d")

            if period is None:
                period = timedelta(seconds=24 * 3600)
            else:
                period = timedelta(seconds=int(period))

            end_time = start_time - period

            print("Start Time", start_time)
            print("End Time", end_time)
            print("Period", period)

            qs = qs.objects.filter(when__gte=end_time, when__lte=start_time)
        else:
            qs = qs.all()

        return qs.order_by('-when')


class Send(LoginRequiredMixin, CreateView):
    model = Notification
    form_class = NotificationForm
    template_name = "backend/notifications/form.html"
    success_url = reverse_lazy('notifications')
