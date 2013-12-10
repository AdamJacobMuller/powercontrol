from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from powercontrol.models import Port, Device, Set
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_backends

from functools import wraps

import logging
import urllib2
import base64
import power.settings
import json

logger = logging.getLogger(__name__)


def do_http_auth(function):
    @wraps(function)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated():
            try:
                auth = request.META['HTTP_AUTHORIZATION']
                auth_parts = auth.split(" ")
                if auth_parts[0] != "Basic":
                    print "bad Authorization header %s" % (auth)
                    return HttpResponseRedirect(power.settings.LOGIN_URL)
                auth_up = base64.b64decode(auth_parts[1]).split(":", 2)
                auth_result = authenticate(username=auth_up[0], password=auth_up[1])
                if auth_result is None:
                    return HttpResponseRedirect(power.settings.LOGIN_URL)
            except KeyError:
                print "no Authorization header"
                return HttpResponseRedirect(power.settings.LOGIN_URL)
        return function(request, **kwargs)
    return _wrapped_view


@login_required
def home(request):
    options = [
        {'name': "Ports", 'href': '/ports'},
        {'name': "Sets", 'href': '/sets'}
    ]
    return render_to_response("index.html", {"options": options})


@login_required
def ports(request, json=False):
    ports = Port.objects.all().exclude(description = '').filter(device__enabled = True)
    return render_to_response("ports.html", {"ports": ports})


@login_required
def port(request, tag, json = False):
    port = get_object_or_404(Port, tag = tag)
    return render_to_response("port.html", {"port": port})


@do_http_auth
def set_port_state(request, tag, state):
    port = get_object_or_404(Port, tag = tag)
    if state == "on":
        port.state = True
    elif state == "off":
        port.state = False
    else:
        raise Exception("invalid port state!")

    rv = port.save()

    return HttpResponse(rv)


@login_required
def sets(request, json = False):
    sets = Set.objects.all()
    for set in sets:
        trues = 0
        falses = 0
        for port in set.ports.all():
            if port.state is True:
                trues += 1
            elif port.state is False:
                falses += 1
        if trues > 0 and falses > 0:
            set.state = "Mixed"
        elif trues > 0 and falses == 0:
            set.state = "On"
        elif trues == 0 and falses > 0:
            set.state = "Off"
        else:
            set.state = "WTF"
    return render_to_response("sets.html", {"sets": sets})


@login_required
def set(request, tag, json=False):
    return HttpResponse('set not implemented')


@do_http_auth
def set_port_mode(request, tag, mode):
    port = get_object_or_404(Port, tag = tag)
    port.mode = mode
    rv = port.save()
    return HttpResponse(rv)


@do_http_auth
def set_set_mode(request, tag, mode):
    set = get_object_or_404(Set, tag = tag)
    rv = []
    for port in set.ports.all():
        port.mode = mode
        rv.append(port.save())

    return HttpResponse(','.join(rv))


@do_http_auth
def set_set_state(request, tag, state):
    set = get_object_or_404(Set, tag = tag)
    rv = []
    for port in set.ports.all():
        if state == "on":
            port.state = True
        elif state == "off":
            port.state = False
        else:
            raise Exception("invalid port state!")

        rv.append(port.save())

    return HttpResponse(','.join(rv))
