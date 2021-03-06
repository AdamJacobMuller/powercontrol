from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'powercontrol.views.home', name='home'),

    url(r'^ports(?P<json>\.json)?$', 'powercontrol.views.ports', name='ports'),
    url(r'^port/(?P<tag>[a-z0-9-]+)(?P<json>\.json)?$', 'powercontrol.views.port', name='port'),
    url(r'^port/(?P<tag>[a-z0-9-]+)/state/(?P<state>on|off)$', 'powercontrol.views.set_port_state', name='port'),
    url(r'^port/(?P<tag>[a-z0-9-]+)/mode/(?P<mode>on|off|none)$', 'powercontrol.views.set_port_mode', name='port'),

    url(r'^sets(?P<json>.json)?$', 'powercontrol.views.sets', name='sets'),
    url(r'^set/(?P<tag>[a-z0-9-]+)(?P<json>\.json)?$', 'powercontrol.views.set', name='set'),
    url(r'^set/(?P<tag>[a-z0-9-]+)/state/(?P<state>on|off)$', 'powercontrol.views.set_set_state', name='set'),
    url(r'^set/(?P<tag>[a-z0-9-]+)/mode/(?P<mode>on|off|none)$', 'powercontrol.views.set_set_mode', name='set'),
    
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout'),
)
