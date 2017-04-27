from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from . import views
from .views import clients, syncs, endpoints, games

admin.site.site_header = "RPS Admin"
admin.site.site_title = "RPS Admin"
admin.site.index_title = "Admin Dashboards"

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),

    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),

    url(r'^dashboard$', views.dashboard, name='dashboard'),

    url(r'^clients$', clients.Index.as_view(), name='clients'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)$', clients.Show.as_view(), name='show_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/delete$', clients.Delete.as_view(), name='delete_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/send$', clients.Send.as_view(), name='send_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/clone/(?P<cid>[a-f0-9\-]+)$', clients.Clone.as_view(), name='clone_client'),

    url(r'^syncs$', syncs.index, name='syncs'),

    url(r'^endpoints$', endpoints.Index.as_view(), name='endpoints'),
    url(r'^endpoints/new$', endpoints.Create.as_view(), name='new_endpoint'),
    url(r'^endpoints/(?P<pk>\d+)$', endpoints.Update.as_view(), name='edit_endpoint'),
    url(r'^endpoints/(?P<pk>\d+)/delete$', endpoints.Delete.as_view(), name='delete_endpoint'),

    url(r'^games$', games.Index.as_view(), name='games'),
    url(r'^games/(?P<pk>\d+)$', games.Show.as_view(), name='show_game'),

    url(r'^$',  RedirectView.as_view(url='dashboard', permanent=False), name='home'),
]
