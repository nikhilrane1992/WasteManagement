# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms import ModelChoiceField
from django import forms

# Register your models here.
admin.site.site_header = 'Admin Waste Management'

class UserChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return '%s  %s - %s' % (obj.first_name, obj.last_name, obj.username)

class WardAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WardAdminForm, self).__init__(*args, **kwargs)
        self.fields['supervisor'] = UserChoiceField(queryset=User.objects.all())

class WardAdmin(admin.ModelAdmin):
    form = WardAdminForm

# Register your models here.
admin.site.register(Enquiry)
admin.site.register(Ward, WardAdmin)
admin.site.register(State)
admin.site.register(City)
admin.site.register(OtpAuthenticator)
# admin.site.register(User)
