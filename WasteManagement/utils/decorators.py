import json
from django.http import JsonResponse
from utils.helper_functions import validate_email, validate_mobile

def is_login_valid(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return function(request, *args, **kwargs)
        else:
            return JsonResponse({
                "validation": "Login details invalid",
                "status": False
            })

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def validate_registration_details(function):
    def wrap(request, *args, **kwargs):
        try:
            obj = json.loads(request.body)
        except:
            return JsonResponse({
                "validation":"Invalid json request",
                "status":False
            })
        if obj.get('mobile_no') and not validate_mobile(obj.get('mobile_no')):
            return JsonResponse({
                "validation":"Mobile number not in valid format",
                "status":False
            })
        else:
            return function(request, *args, **kwargs)


    wrap.__doc__=function.__doc__
    wrap.__name__=function.__name__
    return wrap
