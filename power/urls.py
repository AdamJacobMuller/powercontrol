from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'powercontrol.views.home', name='home'),
    url(r'^ports$', 'powercontrol.views.ports', name='ports'),
    url(r'^port/(?P<tag>[a-z0-9-]+)$', 'powercontrol.views.port', name='port'),
    url(r'^port/(?P<tag>[a-z0-9-]+)/state/(?P<state>on|off)$', 'powercontrol.views.set_state', name='port'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
