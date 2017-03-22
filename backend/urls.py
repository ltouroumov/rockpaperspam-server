from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from .views import clients

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),

    url(r'^login$', views.login_view),
    url(r'^logout$', auth_views.auth_logout),

    url(r'^dashboard$', views.dashboard, name='dashboard'),

    url(r'^clients$', clients.index, name='clients'),
    url(r'^clients/(?P<client_id>[a-f0-9\-]+)$', clients.show, name='show_client'),

    url(r'^$',  RedirectView.as_view(url='dashboard', permanent=False), name='home'),
]
