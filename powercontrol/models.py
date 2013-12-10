from django.db import models

import urllib2
import base64


class Device(models.Model):
    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField(unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    enabled = models.BooleanField()
    type = models.CharField(max_length=255)

    def __unicode__(self):

        if len(self.name) > 0:
            return '%s @ %s' % (self.name, self.ip)
        else:
            return self.ip


class Port(models.Model):
    modes = (
            ('None' , None),
            ('On'   , 'on'),
            ('Off'  , 'off')
    )
    device = models.ForeignKey(Device)
    port = models.IntegerField()
    description = models.CharField(max_length=255)
    tag = models.CharField(unique=True, max_length=255, null=True)
    state = models.BooleanField()
    mode = models.CharField(max_length=255, choices=modes, null=True)

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
        if self.mode == "none":
            self.mode = None
        if self.mode is None:
            if self.state is True:
                d_state = "on"
                v_state = 1
            elif self.state is False:
                d_state = 'off'
                v_state = 1
        else:
            if self.mode == "on":
                d_state = "on"
                v_state = 1
            elif self.mode == "off":
                d_state = 'off'
                v_state = 1
            else:
                raise Exception("invalid mode: %s" % self.mode)
        if self.device.type == "dli":
            url = "http://%s/outlet?%s=%s" % (
                self.device.ip,
                self.port,
                d_state.upper()
            )
            request = urllib2.Request(url = url)
            request.add_header("Authorization",
                               "Basic %s" % (
                               base64.encodestring("%s:%s" % ( self.device.username, self.device.password))
                               )
                               )

            response = urllib2.urlopen(request).read()
        if self.device.type == "vera":
            url = 'http://%s/data_request?id=action&output_format=json&DeviceNum=%d&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue=%d' % (
                self.device.ip,
                self.port,
                v_state
            )
            requests.get(url)
            log.debug(requests.json())

        super(Port, self).save(*args, **kwargs)
        return rv


class Set(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255)
    ports = models.ManyToManyField("Port")

    def __unicode__(self):
        return "Port Set %s" % (self.name)
