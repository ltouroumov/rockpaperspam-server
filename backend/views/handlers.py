from django.shortcuts import render


def not_found(request):
    return render(request, 'backend/not_found.html', context=request, status=404)


def server_error(request):
    return render(request, 'backend/server_error.html', context=request, status=500)

