from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^sync$', views.sync),
    url(r'^friends$', views.friends),
    url(r'^games$', views.games),
    url(r'^games/start$', views.start),
    url(r'^games/(?P<pk>\d+)$', views.game),
    url(r'^games/(?P<pk>\d+)/(?P<rid>\d+)$', views.play),
]
