# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import os, re
from WasteManagement.settings import BASE_DIR
from time import time
import datetime
from django.utils import timezone
from utils.helper_functions import send_complete_enquiry_SMS, send_reject_enquiry_SMS, get_user_profile, send_enquiry_registerd_SMS
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
import json


def upload_document(instance, filename):
    extension = os.path.splitext(filename)[1]
    orginal_file_path = os.path.splitext(filename)[0][:10]
    updated_file_path = "%s_%s" %(re.sub('[^a-zA-Z0-9 \.\_]', '', orginal_file_path).replace(' ', ''),  str(time()).replace('.','_'))
    filename = os.path.join(updated_file_path + extension)

    if not os.path.isdir(BASE_DIR + '/Media'):
        os.makedirs(BASE_DIR + '/Media')
    return os.path.join("%s" %(re.sub('[^a-zA-Z0-9 \.\_]', '', filename).replace(' ', ''), ))


class UserProfile(models.Model):
    STATUS = (
        (0, "English"),
        (1, "Marathi")
    )
    user = models.ForeignKey("auth.User")
    language = models.IntegerField(choices=STATUS, default=0)
    
    def __unicode__(self):
        return "{} - {} - {}".format(self.user.first_name+' '+self.user.last_name, self.get_language_display(), self.user.username)


class State(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return "{}".format(self.name)


class City(models.Model):
    name = models.CharField(max_length=100)
    pincode = models.IntegerField()
    state = models.ForeignKey(State)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return "{} <- city - state -> {}".format(self.name, self.state.name)


class Ward(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City)
    supervisor = models.ForeignKey("auth.User")
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} - {}".format(self.name, self.supervisor.first_name)

    def __get_json__(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": {
                "name": self.city.name,
                "state": self.city.state.name,
                "pincode": self.city.pincode,
            },
            "supervisor": {
                "first_name": self.supervisor.first_name,
                "last_name": self.supervisor.last_name
            },
            "created": int(self.created.strftime('%s')) * 1000,
            "modified": int(self.modified.strftime('%s')) * 1000
        }


class SubWard(models.Model):
    ward = models.ForeignKey(Ward)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} - {}".format(self.name, self.ward.name)

    def __get_json__(self):
        return {
            "id": self.id,
            "name": self.name,
            "ward": self.ward.__get_json__(),
            "created": int(self.created.strftime('%s')) * 1000,
            "modified": int(self.modified.strftime('%s')) * 1000
        }


class Enquiry(models.Model):
    STATUS = (
        (4, "Inprogress"),
        (1, "Completed"),
        (2, "Cancelled"),
        (3, "Enquiry Registered")
    )
    user = models.ForeignKey("auth.User")
    sub_ward = models.ForeignKey(SubWard)
    mobile_no = models.CharField(max_length=12)
    location_pic = models.FileField(upload_to=upload_document, max_length=400)
    status = models.IntegerField(choices=STATUS, default=3)
    address = models.TextField()
    lat = models.FloatField()
    lang = models.FloatField()
    title = models.CharField(max_length=50)
    content = models.TextField()
    comment = models.TextField(null=True, blank=True)
    comment_pic = models.FileField(upload_to=upload_document, max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{} - {} - Status--> {}".format(self.user.first_name, self.user.last_name, self.get_status_display())

    def __get_json__(self):
        return {
            "id": self.id,
            "user": {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "mobile_no": self.user.username
            },
            "sub_ward": self.sub_ward.__get_json__(),
            "mobile_no": self.mobile_no,
            "location_pic": 'Media/'+str(self.location_pic),
            "comment_pic": 'Media/'+str(self.location_pic),
            "comment": self.comment,
            "status": self.get_status_display(),
            "status_id": self.status,
            "address": self.address,
            "lat": self.lat,
            "lang": self.lang,
            "title": self.title     ,
            "content": self.content,
            "created": int(self.created.strftime('%s')) * 1000,
            "modified": int(self.modified.strftime('%s')) * 1000
        }

    def send_enquiry_SMS(self):
        if self.status == 1:
            send_complete_enquiry_SMS(self)
        if self.status == 2:
            send_reject_enquiry_SMS(self)
        if self.status == 3:
            send_enquiry_registerd_SMS(self)
    


class OtpAuthenticator(models.Model):
    otp = models.IntegerField()
    user = models.ForeignKey("auth.User")
    otp_expiry = models.DateTimeField(auto_now_add=True)

    def is_verify(self, user_otp):
        if self.otp_expiry + datetime.timedelta(seconds=600) > timezone.now():
            if (self.otp == int(user_otp.strip())):
                return {"status": True, "validation": "OTP authenticated successfully"}
            else:
                return {"status": False, "validation": "Enter correct OTP"}
        else:
            return {"status": False, "validation": "OTP is expire please try again"}


class SMSLogs(models.Model):
    logs = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{}".format(json.loads(self.logs))


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def update_stock(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)