# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.contrib import admin

# Register your models here.
admin.site.site_header = 'Admin Waste Management'

# Register your models here.
admin.site.register(Enquiry)
admin.site.register(Ward)
admin.site.register(State)
admin.site.register(City)