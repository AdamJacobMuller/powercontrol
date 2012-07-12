from django.template import Context, loader
from django.shortcuts import render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from powercontrol.models import Port,Device
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

import logging
import urllib2
import base64
import power.settings

logger = logging.getLogger(__name__)

@login_required
def home(request):
    options=[
        {'name':"Ports",'href':'/ports'},
        {'name':"Sets",'href':'/sets'}
    ]
    return render_to_response("index.html",{"options":options})
@login_required
def ports(request):
    ports=Port.objects.all().exclude(description='').filter(device__enabled=True)
    return render_to_response("ports.html",{"ports":ports})
@login_required
def port(request,tag):
    port=get_object_or_404(Port,tag=tag)
    return render_to_response("port.html",{"port":port})

def set_port_state(request,tag,state):
    if not request.user.is_authenticated():
        try:
            auth=request.META['HTTP_AUTHORIZATION']
            auth_parts=auth.split(" ")
            if auth_parts[0]!="Basic":
                print "bad Authorization header %s" % (auth)
                return HttpResponseRedirect(power.settings.LOGIN_URL)
            auth_up=base64.b64decode(auth_parts[1]).split(":",2)
            auth_result=authenticate(username=auth_up[0], password=auth_up[1])
            if auth_result is None:
                return HttpResponseRedirect(power.settings.LOGIN_URL)
        except KeyError:
            print "no Authorization header"
            return HttpResponseRedirect(power.settings.LOGIN_URL)
    port=get_object_or_404(Port,tag=tag)
    if state=="on":
        port.state=True
        rv="on"
    elif state=="off":
        port.state=False
        rv="off"
    else:
        raise Exception("invalid port state!")

    request=urllib2.Request(url="http://%s/outlet?%s=%s" % (
        port.device.ip,
        port.port,
        rv.upper()
        ))
    request.add_header("Authorization",
        "Basic %s" % (
            base64.encodestring("%s:%s" % ( port.device.username,port.device.password))
            ))
    response=urllib2.urlopen(request).read()
    port.save()

    return HttpResponse(rv)
def sets(request):
    return HttpResponse('sets not implemented')
def set(request,tag):
    return HttpResponse('set not implemented')
def set_set_state(request,tag,state):
    return HttpResponse('set set not implemented')
