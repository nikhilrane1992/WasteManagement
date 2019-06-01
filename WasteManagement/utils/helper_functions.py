import random, string, datetime
import re

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
