from django.db import models

import urllib2
import base64
# Create your models here.

class Device(models.Model):
    name        = models.CharField(max_length=255)
    ip          = models.GenericIPAddressField(unique=True)
    username    = models.CharField(max_length=255)
    password    = models.CharField(max_length=255)
    enabled     = models.BooleanField()
    type        = models.CharField(max_length=255)

    def __unicode__(self):

        if len(self.name)>0:
            return '%s @ %s' % (self.name,self.ip)
        else:
            return self.ip


class Port(models.Model):
    modes       = (
                    ('None' , None),
                    ('On'   , 'on'),
                    ('Off'  , 'off')
                    )
    device      = models.ForeignKey(Device)
    port        = models.IntegerField()
    description = models.CharField(max_length=255)
    tag         = models.CharField(unique=True, max_length=255, null=True)
    state       = models.BooleanField()
    mode        = models.CharField(max_length=255, choices=modes, null=True)

    def __unicode__(self):
        if len(self.device.name)>0:
            dn=self.device.name
        else:
            dn=self.device.ip

        if len(self.description)>0:
            pn="%s (Port %s)" % (self.description,self.port)
        else:
            pn="Port %s" % (self.port)

        return "%s - %s" % (dn,pn)

    def save(self, *args, **kwargs):
        if self.mode is None:
            if self.state == True:
                rv="on"
            elif self.state == False:
                rv="off"
        else:
            if self.mode == "on":
                rv="on"
            elif self.mode == "off":
                rv="off"
            else:
                raise Exception("invalid RV value")
        url = "http://%s/outlet?%s=%s" % (
            self.device.ip,
            self.port,
            rv.upper()
            )
        request=urllib2.Request(url=url)
        request.add_header("Authorization",
            "Basic %s" % (
                base64.encodestring("%s:%s" % ( self.device.username, self.device.password))
                ))
        response=urllib2.urlopen(request).read()
        super(Port, self).save(*args, **kwargs)
        return rv

class Set(models.Model):
    name        = models.CharField(max_length=255)
    tag         = models.CharField(max_length=255)
    ports       = models.ManyToManyField("Port")

    def __unicode__(self):
        return "Port Set %s" % (self.name)
