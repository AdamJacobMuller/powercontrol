from django.template import Context, loader
from django.shortcuts import render_to_response,get_object_or_404
from django.http import HttpResponse
from powercontrol.models import Port,Device
import logging
import urllib2
import base64

logger = logging.getLogger(__name__)


def home(request):
    options=[
        {'name':"Ports",'href':'/ports'}
    ]
    return render_to_response("index.html",options)
def ports(request):
    ports=Port.objects.all().exclude(description='').filter(device__enabled=True)
    return render_to_response("ports.html",{"ports":ports})
def port(request,tag):
    port=get_object_or_404(Port,tag=tag)
    return render_to_response("port.html",{"port":port})
def set_state(request,tag,state):
    port=get_object_or_404(Port,tag=tag)
    if state=="on":
        port.state=True
        rv="on"
    elif state=="off":
        port.state=False
        rv="off"
    else:
        raise Exception("invalid port state!")
    port.save()

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

    return HttpResponse(rv)
