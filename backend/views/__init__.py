from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from api.models import Client, Sync, Game
from backend.models import Endpoint


def login_view(request: HttpRequest):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if 'next' in request.GET:
                next = request.GET['next']
            else:
                next = '/dashboard'

            return redirect(to=next)
        else:
            return render(request, "backend/login.html", {
                'error': 'Incorrect Login'
            })
    else:
        return render(request, "backend/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect(to='login')


@login_required
def dashboard(request):
    from datetime import datetime, timedelta
    last_24h = datetime.now() - timedelta(seconds=24 * 3600)

    client_count = Client.objects.count()
    sync_count = Sync.objects.filter(date__gte=last_24h).count()
    endpoint_count = Endpoint.objects.count()
    game_count = Game.objects.count()

    return render(request, "backend/dashboard.html", {
        'client_count': client_count,
        'sync_count': sync_count,
        'endpoint_count': endpoint_count,
        'game_count': game_count,
    })
