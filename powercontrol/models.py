from django.db import models

# Create your models here.

class Device(models.Model):
    ip          = models.GenericIPAddressField(unique=True)
    username    = models.CharField(max_length=255)
    password    = models.CharField(max_length=255)
    enabled     = models.BooleanField()
    type        = models.CharField(max_length=255)
    def __unicode__(self):
        return self.ip


class Port(models.Model):
    device      = models.ForeignKey(Device)
    port        = models.IntegerField()
    description = models.CharField(max_length=255)
    tag         = models.CharField(unique=True,max_length=255,null=True)
    state       = models.BooleanField()
    def __unicode__(self):
        return "Port %s @ %s (%s)" % ( self.port, self.device.ip,self.description)

class Set(models.Model):
    name        = models.CharField(max_length=255)
    tag         = models.CharField(max_length=255)
    def __unicode__(self):
        return "Port Set %s" % (self.name)

class SetPort(models.Model):
    port        = models.ForeignKey(Port)
    set         = models.ForeignKey(Set)
    def __unicode__(self):
        return "Port %s in set %s" % ( self.port.description, self.set.name )
    class Meta:
        unique_together = (('port','set'))
