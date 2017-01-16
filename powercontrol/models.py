import urllib2
import requests
import base64
import logging

from django.db import models

logger = logging.getLogger("model")


class Device(models.Model):
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    enabled = models.BooleanField()
    type = models.CharField(max_length=255)

    def __unicode__(self):

        if len(self.name) > 0:
            return '%s @ %s' % (self.name, self.ip)
        else:
            return self.ip


class Port(models.Model):
    modes = (
            ('none', None),
            ('on', 'On'),
            ('off', 'Off')
    )
    authorities = (
                  ('local', 'Local'),
                  ('remote', 'Remote'),

    )
    device = models.ForeignKey(Device)
    port = models.IntegerField()
    description = models.CharField(max_length=255)
    tag = models.CharField(unique=True, max_length=255, null=True)
    state = models.BooleanField()
    mode = models.CharField(max_length=255, choices=modes, null=True, blank=True)
    authority = models.CharField(max_length=255, choices=authorities, null=False, default='local')

    def __unicode__(self):
        if len(self.device.name) > 0:
            dn = self.device.name
        else:
            dn = self.device.ip

        if len(self.description) > 0:
            pn = "%s (Port %s)" % (self.description, self.port)
        else:
            pn = "Port %s" % (self.port)

        return "%s - %s" % (dn, pn)

    def save(self, *args, **kwargs):
        print "%s: entering save()" % self
        logger.debug("%s: entering save" % self)
        if self.mode == "none":
            self.mode = None
        if self.mode == "None":
            self.mode = None
        d_state = 'unknown'
        v_state = 'unknown'
        if self.mode is None:
            if self.state is True:
                d_state = "on"
                v_state = 1
            elif self.state is False:
                d_state = 'off'
                v_state = 0
        else:
            if self.mode == "on":
                d_state = "on"
                v_state = 1
            elif self.mode == "off":
                d_state = 'off'
                v_state = 0
            else:
                raise Exception("invalid mode: %s" % self.mode)
        logger.info("mode = %s, state = %s, v_state = %s, d_state = %s" % (self.mode, self.state, v_state, d_state))
        print("mode = %s, state = %s, v_state = %s, d_state = %s" % (self.mode, self.state, v_state, d_state))
        if self.device.type == "dli":
            url = "http://%s/outlet?%s=%s" % (
                self.device.ip,
                self.port,
                d_state.upper()
            )
            request = urllib2.Request(url=url)
            print "%s: making HTTP request to %s" % (self, url)
            request.add_header("Authorization",
                               "Basic %s" % (
                                   base64.encodestring("%s:%s" % (self.device.username, self.device.password))
                               )
                               )

            response = urllib2.urlopen(request, None, 3).read()
            logging.debug("got response from dli: %s" % response)
        elif self.device.type == "vera":
            url = 'http://%s/data_request?id=action&output_format=json&DeviceNum=%d&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=%d' % (
                self.device.ip,
                self.port,
                v_state
            )
            requests.get(url, timeout=3)
        else:
            raise Exception("INVALID DEVICE TYPE!")
        if self.state is None:
            self.state = True

        super(Port, self).save(*args, **kwargs)
        return d_state


class Set(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    ports = models.ManyToManyField("Port")

    def __unicode__(self):
        return "Port Set %s" % (self.name)
