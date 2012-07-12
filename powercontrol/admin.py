from powercontrol.models import *
from django.contrib import admin

class SetAdmin(admin.ModelAdmin):
    filter_horizontal=['ports']

admin.site.register(Device)
admin.site.register(Port)
admin.site.register(Set,SetAdmin)
#admin.site.register(SetPort)
