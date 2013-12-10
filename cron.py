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
    format = '%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger("cron")

parser = OptionParser()
parser.add_option("-l", "--log-level", dest = "log_level", default = "INFO")
parser.add_option("-r", "--reconcile", dest = "reconcile", default = False, action = 'store_true')
parser.add_option("-c", "--christmas", dest = "christmas", default = False, action = 'store_true')
parser.add_option("-f", "--forecast", dest = "forecast", default = False)
parser.add_option("-t", "--time", dest = "time", default = False)

(options, args) = parser.parse_args()

logger.setLevel(getattr(logging, options.log_level))


def clean(string):
    return re.sub("[^a-zA-Z0-9]+", "-", string).strip("-").lower()

if options.reconcile:
    devices = Device.objects.filter(enabled = True).all()
    for device in devices:
        try:
            url = "http://%s/index.htm" % (device.ip)
            request = urllib2.Request(url="http://%s/index.htm" % (device.ip))
            request.add_header("Authorization",
                               "Basic %s" % (
                               base64.encodestring("%s:%s" % ( device.username, device.password))
                               )
                               )
            logger.debug("loading %s" % url)
            response = urllib2.urlopen(request, timeout = 2).read()
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

                port.tag = clean(port.description)
                if len(port.tag) == 0:
                    port.tag = None

                if match.group("state") == "ON":
                    port.state = True
                elif match.group("state") == "OFF":
                    port.state = False
                else:
                    port.state = None
                try:
                    port.save()
                except:
                    logger.error(sys.exc_info()[0])
                logger.debug(port)
        except urllib2.HTTPError as foo:
            logger.error("failed: %s" % ( foo))
        except socket.timeout as foo:
            logger.error("failed: %s" % ( foo))

if options.christmas:
    sun_times = astral.Astral()['New York'].sun(datetime.date.today())
    est = pytz.timezone("America/New_York")
    if options.time:
        now = datetime.datetime.fromtimestamp(float(options.time), tz = est)
    else:
        now = datetime.datetime.now(tz = est)
    sunset = sun_times['sunset']
    sunrise = sun_times['sunrise']
    i_delta = (now - sunrise).total_seconds()

    logger.debug("now is %s (%s)" % (now, repr(now)))
    logger.debug("sunrise is %s (%s)" % (sunset, repr(sunrise)))
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

        f_url = 'https://api.forecast.io/forecast/%s/%f,%f' % ( api_key, lat, lon)

        logger.debug("loading forecast from %s" % f_url)
        forecast = requests.get(f_url)

        if forecast.json['currently']['cloudCover'] > cloudCover:
            logger.debug("cloudCover of %f is > %f" % ( forecast.json['currently']['cloudCover'], cloudCover))
            desired_state = "on"
        else:
            logger.debug("cloudCover of %f is <= %f" % ( forecast.json['currently']['cloudCover'], cloudCover))

        if forecast.json['currently']['visibility'] < visibility:
            logger.debug("visibility of %f is < %f" % ( forecast.json['currently']['visibility'], visibility))
            desired_state = "on"
        else:
            logger.debug("visibility of %f is >= %f" % ( forecast.json['currently']['visibility'], visibility))

    set = get_object_or_404(Set, tag = 'christmas-lights')
    for port in set.ports.all():
        if desired_state == "on":
            if port.state is True:
                logger.debug("%s already on, skipping" % port)
                continue
            port.state = True
        elif desired_state == "off":
            if port.state is False:
                logger.debug("%s already off, skipping" % port)
                continue
            port.state = False
        else:
            raise Exception("invalid port state!")

        port.save()
