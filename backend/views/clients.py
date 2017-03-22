from django.contrib.auth import authenticate, login
from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from api.models import Client


@login_required
def index(request):
    clients = Client.objects.all()
    return render(request, "backend/clients/index.html", {
        'clients': clients
    })


@login_required
def show(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
    except:
        raise Http404("Requested client does not exist")

    return render(request, "backend/clients/show.html", {
        'client': client
    })
