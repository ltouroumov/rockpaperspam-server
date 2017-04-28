from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from api.models import Sync


class Index(LoginRequiredMixin, ListView):
    model = Sync
    template_name = "backend/syncs/index.html"
    paginate_by = 25

    def get_queryset(self):
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

            syncs = Sync.objects.filter(date__gte=end_time, date__lte=start_time)
        else:
            print("All syncs ...")
            syncs = Sync.objects.all()

        return syncs.order_by('-date')
