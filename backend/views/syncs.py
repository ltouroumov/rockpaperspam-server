from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from api.models import Client, Sync


@login_required
def index(request):
    start_time = request.GET.get('start', None)
    period = request.GET.get('period', None)

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

    syncs = Sync.objects.filter(date__gte=end_time, date__lte=start_time).order_by('-date')
    return render(request, "backend/syncs/index.html", {
        'syncs': syncs
    })
