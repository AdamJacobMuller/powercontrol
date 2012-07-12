from django.db import models

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
    device      = models.ForeignKey(Device)
    port        = models.IntegerField()
    description = models.CharField(max_length=255)
    tag         = models.CharField(unique=True,max_length=255,null=True)
    state       = models.BooleanField()
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

class Set(models.Model):
    name        = models.CharField(max_length=255)
    tag         = models.CharField(max_length=255)
    ports       = models.ManyToManyField("Port")
    def __unicode__(self):
        return "Port Set %s" % (self.name)

#class SetPort(models.Model):
#    port        = models.ForeignKey(Port)
#    set         = models.ForeignKey(Set)
#    def __unicode__(self):
#        return "Port %s in set %s" % ( self.port.description, self.set.name )
#    class Meta:
#        unique_together = (('port','set'))
