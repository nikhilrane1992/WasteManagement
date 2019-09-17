# -*- coding: utf-8 -*-
from django.core.files.base import ContentFile
import random, string, datetime
import re
import base64
import requests
from random import randint
from django.contrib.auth.models import User, Group
import json

APIKey = "x6qdYCgMT0CijeDmCuavaQ"
SENDERID = "SMSTST"

def save_sms_log(data):
    from WasteManagement.models import SMSLogs
    SMSLogs.objects.get_or_create(logs=json.dumps(data))


def get_user_profile(user):
    user_profile = user.userprofile_set.get()
    group = Group.objects.filter(user = user).first()
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "group": group.name,
        "language": user_profile.language,
        "language_disp": user_profile.get_language_display(),
    }


def validate_mobile(value):
    rule = re.compile(r'^(\+91[\-\s]?)?[0]?[1789]\d{9}$')
    if not rule.search(value):
        return False
    else:
        if value.startswith("+91"):
            return value[3:]
        elif value.startswith("0"):
            return value[1:]
        else:
            return value


def validate_email(email):
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        return True
    return False


def date_to_epoch(datetime_obj):
    return int(datetime_obj.strftime('%s')) * 1000


def epoch_to_date(epoach):
    return datetime.datetime.fromtimestamp(epoach / 1000)


def id_generator(size=8, chars=string.ascii_uppercase + string.digits+string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def get_file(data):
    format, imgstr = data.split(';base64,') 
    ext = format.split('/')[-1] 
    return ContentFile(base64.b64decode(imgstr), name=id_generator() + '.' + ext) 
  

def generateOTP():
    otp = ""  
    for p in range(0, 6):
        otp+=str(randint(0,9))
    return otp


def send_otp(otp_obj):
    kwargs = {"senderid":"SMSTST", "channel": 2, "number": "91"+otp_obj.user.username, "message": str(otp_obj.otp)+" is your one time password to proceed on Clean City. It is valid for 10 minutes. Do not share your OTP with anyone.", "otp": otp_obj.otp, "dcs": 0}
    send_sms(kwargs)


def send_complete_enquiry_SMS(enquiry):
    user_profile = get_user_profile(enquiry.user)
    dcs = 0 #Encoding format 0 for english and 8 for marathi
    if user_profile['language'] == 0:
        message = "Dear complainant your complaint has been successfully attended. You can look at site photographs/reply on the app. Thanking you, look forward to serving you again!"
    elif user_profile['language'] == 1:
        dcs = 8
        message = "प्रिय उपभोगता आपल्या तक्रारीचे निवारण करण्यात आले आहे. आपण या संबंधीची माहिती अॅप वर पाहू शकता. धन्यवाद, आम्ही सदैव आपल्याला सेवा देण्यास उत्सूक आहोत !!"
    else:
        message = "Not valid for this user"
    kwargs = {"senderid":SENDERID, "channel": 2, "number": "91"+enquiry.user.username, "message": message, "dcs": dcs}
    send_sms(kwargs)


def send_reject_enquiry_SMS(enquiry):
    user_profile = get_user_profile(enquiry.user)
    dcs = 0
    if user_profile['language'] == 0:
        message = "Dear complainant sorry to inform you that your complaint could not be attended because of following reasons : {}. If you have any query please contact our manager on : {}. Or see details on the app.".format(enquiry.comment, enquiry.sub_ward.ward.supervisor.username)
    elif user_profile['language'] == 1:
        dcs = 8
        message = "प्रिय उपभोगता आपणास कळवण्यात येते की खालील कारणा ({}) मुळे आपल्या तक्रारीचे निवारण करण्यात येऊ शकत नाही. तरी आपणास या बाबत काही शंका असल्यास मॅनेजरशी संपर्क साधावा : {}. अथवा अॅप वर माहिती मिळवावी.".format(enquiry.comment, enquiry.sub_ward.ward.supervisor.username)
    else:
        message = "Not valid for this user"
    kwargs = {"senderid":SENDERID, "channel": 2, "number": "91"+enquiry.user.username, "message": message, "dcs": dcs}
    send_sms(kwargs)

def send_enquiry_registerd_SMS(enquiry):
    user_profile = get_user_profile(enquiry.user)
    dcs = 0
    if user_profile['language'] == 0:
        message = "Dear complainant Thank you for your complaint. We have received your enquiry for number {}. For more details check the app.".format(enquiry.mobile_no)
    elif user_profile['language'] == 1:
        dcs = 8
        message = "प्रिया उपभोगता, {} या नंबर करता तुमची तक्रार आम्हाला मिळाली आहे. तक्रार ची अधिक माहिती करता अँप बघा.".format(enquiry.mobile_no)
    else:
        message = "Not valid for this user"
    kwargs = {"senderid":SENDERID, "channel": 2, "number": "91"+enquiry.user.username, "message": message, "dcs": dcs}
    send_sms(kwargs)


def send_sms(kwargs):
    save_sms_log(kwargs)
    kwargs['APIKey'] = APIKey
    url = "https://www.smsgatewayhub.com/api/mt/SendSMS?APIKey={APIKey}&senderid={senderid}&channel={channel}&DCS={dcs}&flashsms=0&number={number}&text={message}&route=clickhere".format(**kwargs)
    r = requests.get(url)