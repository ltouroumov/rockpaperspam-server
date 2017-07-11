from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^register$', views.register),
    url(r'^ping$', views.ping),
    url(r'^status', views.client_status),
    url(r'^sync$', views.sync),
    url(r'^friends$', views.friends),
    url(r'^profile$', views.profile),
    url(r'^games$', views.games),
    url(r'^games/start$', views.start),
    url(r'^games/(?P<pk>\d+)$', views.game),
    url(r'^games/(?P<pk>\d+)/(?P<rid>\d+)$', views.play),
    url(r'^notifications/ack', views.notifications_ack)
]
