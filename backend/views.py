from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


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
def dashboard(request):
    return render(request, "backend/dashboard.html")
