from django.core.files.base import ContentFile
import random, string, datetime
import re
import base64
import requests
from random import randint

APIKey = "x6qdYCgMT0CijeDmCuavaQ"


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


def send_sms(kwargs):
    print kwargs
    kwargs['APIKey'] = APIKey
    url = "https://www.smsgatewayhub.com/api/mt/SendSMS?APIKey={APIKey}&senderid={senderid}&channel={channel}&DCS=0&flashsms=0&number={number}&text={message}&route=clickhere".format(**kwargs)
    print url
    # r = requests.get(url)
    # print r.text