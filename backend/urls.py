from django.conf.urls import include, url, handler404, handler500
from django.contrib import admin
from django.views.generic.base import RedirectView

from . import views
from .views import clients, syncs, endpoints, games, notifications, notification_templates, config

admin.site.site_header = "RPS Admin"
admin.site.site_title = "RPS Admin"
admin.site.index_title = "Admin Dashboards"

handler404 = 'backend.views.handlers.not_found'
handler500 = 'backend.views.handlers.server_error'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),

    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),

    url(r'^dashboard$', views.dashboard, name='dashboard'),

    url(r'^clients$', clients.Index.as_view(), name='clients'),
    url(r'^clients/_create$', clients.Create.as_view(), name='create_client'),
    url(r'^clients/_delete$', clients.DeleteMulti.as_view(), name='delete_multi_clients'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)$', clients.Show.as_view(), name='show_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/_delete$', clients.Delete.as_view(), name='delete_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/_reset', clients.Reset.as_view(), name='reset_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/energy', clients.EditEnergy.as_view(), name='edit_client_energy'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/send$', clients.Send.as_view(), name='send_client'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/contact/_create$', clients.ContactCreate.as_view(), name='create_contact'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/contact/_link$', clients.ContactLink.as_view(), name='link_contact'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/contact/(?P<cid>[a-f0-9\-]+)/clone$', clients.ContactClone.as_view(), name='clone_contact'),
    url(r'^clients/(?P<pk>[a-f0-9\-]+)/contact/(?P<cid>[a-f0-9\-]+)/_delete$', clients.ContactDelete.as_view(), name='delete_contact'),

    url(r'^syncs$', syncs.Index.as_view(), name='syncs'),

    url(r'^endpoints$', endpoints.Index.as_view(), name='endpoints'),
    url(r'^endpoints/new$', endpoints.Create.as_view(), name='new_endpoint'),
    url(r'^endpoints/(?P<pk>\d+)$', endpoints.Update.as_view(), name='edit_endpoint'),
    url(r'^endpoints/(?P<pk>\d+)/_delete$', endpoints.Delete.as_view(), name='delete_endpoint'),

    url(r'^games$', games.Index.as_view(), name='games'),
    url(r'^games/(?P<pk>\d+)$', games.Show.as_view(), name='show_game'),
    url(r'^games/(?P<pk>\d+)/_delete$', games.Delete.as_view(), name='delete_game'),

    url(r'^notifications$', notifications.Index.as_view(), name='notifications'),
    url(r'^notifications/send$', notifications.Send.as_view(), name='send_notification'),

    url(r'^notifications/templates$', notification_templates.Index.as_view(), name='notification_templates'),
    url(r'^notifications/templates/_create$', notification_templates.Create.as_view(), name='create_notification_template'),
    url(r'^notifications/templates/(?P<pk>[^/]+)/_edit', notification_templates.Update.as_view(), name='edit_notification_template'),
    url(r'^notifications/templates/(?P<pk>[^/]+)/_delete', notification_templates.Delete.as_view(), name='delete_notification_template'),

    url(r'^config$', config.Index.as_view(), name='config'),
    url(r'^config/_create$', config.Create.as_view(), name='new_config'),
    url(r'^config/(?P<pk>[^/]+)/_edit$', config.Update.as_view(), name='edit_config'),
    url(r'^config/(?P<pk>[^/]+)/_delete$', config.Delete.as_view(), name='delete_config'),

    url(r'^$',  RedirectView.as_view(url='dashboard', permanent=False), name='home'),
]
