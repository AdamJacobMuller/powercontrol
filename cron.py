import os
import sys
import urllib2
import base64
import re
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "power.settings")

from powercontrol.models import *

def clean(string):
    return re.sub("[^a-zA-Z0-9]+","-",string).strip("-").lower()

devices=Device.objects.all()

for device in devices:
    try:
        request=urllib2.Request(url="http://%s/index.htm" % (device.ip))
        request.add_header("Authorization",
            "Basic %s" % (
                base64.encodestring("%s:%s" % ( device.username,device.password))
            ))
        response=urllib2.urlopen(request).read()
        rer=re.finditer('<tr bgcolor="#F4F4F4"><td align=center>(?P<port>\d+)</td>[\n\t\s]+<td>(?P<description>.*?)</td><td>[\n\t\s]+<b><font color=(?:green|red)>(?P<state>ON|OFF)</font></b></td>',response)
        for match in rer:
            ports=Port.objects.filter(
                device=device,
                port=match.group("port")
                )
            if len(ports)==0:
                port=Port()
                port.port=match.group("port")
                port.device=device
            else:
                port=ports[0]

            port.description=match.group("description")

            port.tag=clean(port.description)
            if len(port.tag)==0:
                port.tag=None

            if match.group("state")=="ON":
                port.state=True
            elif match.group("state")=="OFF":
                port.state=False
            else:
                port.state=None
            try:
                port.save()
            except:
                print sys.exc_info()[0]
            print port
    except urllib2.HTTPError as foo:
        print "failed: %s" % ( foo[0] )
