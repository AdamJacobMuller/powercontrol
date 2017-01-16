#!/usr/bin/python2.7
import os
import sys
import urllib2
import base64
import re
import datetime
import pytz
import astral
import socket
import logging
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "power.settings")

from powercontrol.models import *
from django.shortcuts import get_object_or_404
from optparse import OptionParser

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger("cron")

parser = OptionParser()
parser.add_option("-l", "--log-level", dest="log_level", default="INFO")
parser.add_option("-r", "--reconcile", dest="reconcile", default=False, action='store_true')
parser.add_option("-c", "--christmas", dest="christmas", default=False, action='store_true')
parser.add_option("-f", "--forecast", dest="forecast", default=False)
parser.add_option("-t", "--time", dest="time", default=False)

(options, args) = parser.parse_args()

logger.setLevel(getattr(logging, options.log_level))


def clean(string, id=None, port=None):
    tag = re.sub("[^a-zA-Z0-9]+", "-", string).strip("-").lower()
    if port is not None:
        ports = Port.objects.filter(
            tag=tag
        )
        #logger.debug("clean: ports is %s" % ports)
        if id is None or ports[0].id != id:
            return '%s-%s' % (tag, port)
#    else:
#        logger.debug("clean: no lookup for %s - %s - %s" % (string, id, port))
    return tag

if options.reconcile:
    devices = Device.objects.filter(enabled=True).all()
    for device in devices:
        if device.type == "dli":
            try:
                url = "http://%s/index.htm" % (device.ip)
                request = urllib2.Request(url="http://%s/index.htm" % (device.ip))
                request.add_header("Authorization",
                                   "Basic %s" % (
                                       base64.encodestring("%s:%s" % (device.username, device.password))
                                   )
                                   )
                logger.info("%s: loading %s" % (device, url))
                response = urllib2.urlopen(request, timeout=2).read()
                rer = re.finditer('<tr bgcolor="#F4F4F4"><td align=center>(?P<port>\d+)</td>[\n\t\s]+<td>(?P<description>.*?)</td><td>[\n\t\s]+<b><font color=(?:green|red)>(?P<state>ON|OFF)</font></b></td>', response)
                for match in rer:
                    ports = Port.objects.filter(
                        device=device,
                        port=match.group("port")
                    )
                    if len(ports) == 0:
                        port = Port()
                        port.port = match.group("port")
                        port.device = device
                    else:
                        port = ports[0]

                    port.description = match.group("description")

                    logger.error("%s authority is %s" % (port, port.authority))

                    port.tag = clean(port.description)
                    if len(port.tag) == 0:
                        port.tag = None

                    if match.group("state") == "ON" and port.state is False:
                        if port.authority == "remote":
                            logger.error("%s: local port state was off, remote port state is on, authority is remote" % port)
                            port.state = True
                        elif port.authority == "local":
                            logger.error("%s: local port state was off, remote port state is on, authority is local" % port)
                    elif match.group("state") == "OFF" and port.state is True:
                        if port.authority == "remote":
                            logger.error("%s: local port state was on, remote port state is off, authority is remote" % port)
                            port.state = False
                        elif port.authority == "local":
                            logger.error("%s: local port state was on, remote port state is off, authority is local" % port)

                    try:
                        logger.debug("%s: calling save()" % port)
                        port.save()
                    except Exception as e:
                        logger.exception(e)
            except urllib2.URLError as foo:
                logger.exception(foo)
            except urllib2.HTTPError as foo:
                logger.exception(foo)
            except socket.timeout as foo:
                logger.exception(foo)
        elif device.type == "vera":
            try:
                s_url = "http://%s/data_request?id=sdata&output_format=json" % device.ip
                logger.info("%s: loading %s" % (device, s_url))
                sdata = requests.get(s_url)
                s_json = sdata.json()
                for vera_device in s_json['devices']:
                    ports = Port.objects.filter(
                        device=device,
                        port=vera_device['id']
                    )
                    if len(ports) == 0:
                        port = Port()
                        port.port = vera_device['id']
                        port.device = device
                    else:
                        port = ports[0]

                    port.description = vera_device['name']

                    port.tag = clean(port.description, port.id, port.port)

                    if 'status' not in vera_device:
                        logger.info("skipping device %s because it has no status" % vera_device['name'])
                        continue

                    if vera_device['status'] == "1":
                        port.state = True
                    elif vera_device['status'] == "0":
                        port.state = False
                    else:
                        raise Exception("unknown vera device status: %s" % (repr(vera_device['status'])))

                    if len(port.tag) == 0:
                        port.tag = None
                    try:
                        port.save()
                    except Exception as e:
                        logger.exception(e)
            except Exception as e:
                logger.exception("caught exception handling device = %s" % vera_device)

if options.christmas:
    sun_times = astral.Astral()['New York'].sun(datetime.date.today())
    est = pytz.timezone("America/New_York")
    if options.time:
        now = datetime.datetime.fromtimestamp(float(options.time), tz=est)
    else:
        now = datetime.datetime.now(tz=est)
    sunset = sun_times['sunset']
    sunrise = sun_times['sunrise']
    i_delta = (now - sunrise).total_seconds()

    logger.debug("now is %s (%s)" % (now, repr(now)))
    logger.debug("sunrise is %s (%s)" % (sunrise, repr(sunrise)))
    logger.debug("sunset is %s (%s)" % (sunset, repr(sunset)))
    logger.debug("now-rise delta is %s (%s) %s" % (now - sunrise, repr(now - sunrise), i_delta))

    if now > sunset:
        logger.info("currently after sunset")
        desired_state = "on"
    elif i_delta > -3600 and i_delta < 1800:
        logger.info("currently around sunrise")
        desired_state = "on"
    else:
        logger.info("not after sunset")
        desired_state = "off"

    if options.forecast and desired_state == "off" and i_delta > 0:
        f_opts = options.forecast.split(",")
        api_key = f_opts[0]
        lat = float(f_opts[1])
        lon = float(f_opts[2])
        try:
            cloudCover = float(f_opts[3])
        except IndexError:
            cloudCover = .75
        try:
            visibility = float(f_opts[4])
        except IndexError:
            visibility = 1

        f_url = 'https://api.forecast.io/forecast/%s/%f,%f' % (api_key, lat, lon)

        logger.debug("loading forecast from %s" % f_url)
        forecast = requests.get(f_url)
        forecast_j = forecast.json()

        if forecast_j['currently']['cloudCover'] > cloudCover:
            logger.info("cloudCover of %f is > %f" % (forecast_j['currently']['cloudCover'], cloudCover))
            desired_state = "on"
        else:
            logger.debug("cloudCover of %f is <= %f" % (forecast_j['currently']['cloudCover'], cloudCover))

        if forecast_j['currently']['visibility'] < visibility:
            logger.info("visibility of %f is < %f" % (forecast_j['currently']['visibility'], visibility))
            desired_state = "on"
        else:
            logger.debug("visibility of %f is >= %f" % (forecast_j['currently']['visibility'], visibility))

    christmas_lights = get_object_or_404(Set, tag='christmas')
    for port in christmas_lights.ports.all():
        if port.device.enabled is False:
            continue
        if desired_state == "on":
            if port.state is True:
                logger.debug("%s already on, skipping" % port)
                continue
            port.state = True
            logger.info("%s: turning port on" % port)
        elif desired_state == "off":
            if port.state is False:
                logger.debug("%s already off, skipping" % port)
                continue
            port.state = False
            logger.info("%s: turning port off" % port)
        else:
            raise Exception("invalid port state!")
        try:
            port.save()
        except Exception as e:
            logger.exception(e)
