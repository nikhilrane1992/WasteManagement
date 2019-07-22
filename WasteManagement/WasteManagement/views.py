import json
from django.contrib import auth
from django.http import JsonResponse
from utils.decorators import is_login_valid, validate_registration_details
from models import Enquiry, Ward, OtpAuthenticator
from utils.helper_functions import epoch_to_date, validate_mobile, get_file, generateOTP
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

def user_dict(user):
    group = Group.objects.filter(user = user).first()
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "group": group.name
    }


def is_user_logged_in(request):
    if request.user.is_authenticated():
        return JsonResponse({
            "validation": "Login Successfull",
            "status": True,
            "user": user_dict(request.user)
        })
    else:
        return JsonResponse({
            "validation": "Invalid login",
            "status": False
        })


def send_otp_message(request):
    params = json.loads(request.body)
    otp = generateOTP()
    if not validate_mobile(params['mobile_no']):
        return JsonResponse({
            "validation": "Mobile number not in valid format",
            "status": False
        })
    
    try:
        user = User.objects.get(username=params['mobile_no'])
    except ObjectDoesNotExist:
        return JsonResponse({
            "validation": "This user not registered in our system",
            "status": False
        })
    otp_authenticator, created = OtpAuthenticator.objects.update_or_create(user=user, defaults={"otp": otp.strip(), "otp_expiry": datetime.now()})
    otp_authenticator.send_otp()
    return JsonResponse({
        "validation": "OTP sent successfully",
        "status": False
    })

def forgot_password(request):
    params = json.loads(request.body)
    confirm_password = params['confirm_password']
    password = params['password']
    otp_authenticator = OtpAuthenticator.objects.filter(user__username=params['mobile_no']).first()
    if not otp_authenticator:
        return JsonResponse({
            "validation": "This user not registered in our system",
            "status": False
        })
    user = otp_authenticator.user
    otp_verify_obj = otp_authenticator.is_verify(params['otp'])
    if otp_verify_obj['status']:
        if password != confirm_password:
            return JsonResponse({
                "validation": "Password not match with confirm password",
                "status": False
            })
        user.set_password(password)
        user.save()
        return JsonResponse({
            "validation": "Password changed successfully",
            "status": True
        })
    else:
        return JsonResponse(otp_verify_obj)


def auth_view(request):
    dict = json.loads(request.body)

    username = dict['username']
    password = dict['password']

    if not validate_mobile(username):
        return JsonResponse({
            "validation": "Mobile number not in valid format",
            "status": False
        })
    user = auth.authenticate(username=username, password=password)

    group = Group.objects.filter(user=user).first()
    if not group:
        return JsonResponse({
            "validation": "User not in any operational group",
            "status": False,
        })

    if user is not None:
        auth.login(request, user)
        return JsonResponse({
            "validation": "Login Successfull",
            "status": True,
            "user": user_dict(user)
        })
    else:
        return JsonResponse({
            "validation": "This user not registered in our system",
            "status": False
        })


def register_user(request):
    dict = json.loads(request.body)

    username = dict['mobile_no']
    password = dict['password']
    confirm_password = dict['confirm_password']

    if not validate_mobile(username):
        return JsonResponse({
            "validation": "Mobile number not in valid format",
            "status": False
        })

    if password != confirm_password:
        return JsonResponse({
            "validation": "Password not match with confirm password",
            "status": False
        })
    user, created = User.objects.get_or_create(first_name=dict['first_name'], 
                                last_name=dict['last_name'],username=username)

    
    group, created = Group.objects.get_or_create(name='CUSTOMER') 
    group.user_set.add(user)

    if user is not None:
        user.set_password(password)
        user.save()
        auth.login(request, user)
        return JsonResponse({
            "validation": "Registered Successfull",
            "status": True,
            "user": user_dict(user)
        })
    else:
        return JsonResponse({
            "validation": "User not registered",
            "status": False
        })

def logout_view(request):
    auth.logout(request)
    return JsonResponse({
        "status": True,
        "validation": "Logout successfull"
    })


def get_filters(request):
    params = json.loads(request.body)
    kwargs = {}
    if params.get('group') and params.get('group') == "CUSTOMER":
        kwargs["user__username"] = request.user
    
    if params.get('group') and params.get('group') == "SUPERVISOR":
        kwargs["ward__supervisor__username"] = request.user

    if params.get('city'):
        kwargs['ward__city__name'] = params.get('city')

    if params.get('user'):
        kwargs['user__username'] = params.get('user')
    
    if params.get('status'):
        kwargs['status'] = params.get('status')
    
    if params.get('date'):
        date = epoch_to_date(params.get('date'))
        kwargs['created__day'] = date.day
        kwargs['created__month'] = date.month
        kwargs['created__year'] = date.year
    
    return kwargs


## Get user enquires
@is_login_valid
def get_user_enquires(request):
    kwargs = get_filters(request)
    enquires = Enquiry.objects.filter(**kwargs)
    enquires_list = []
    for enquiry in enquires:
        enquires_list.append(enquiry.__get_json__())
    
    return JsonResponse({
        "status": True,
        "data": enquires_list
    })


## Create enquiry entry
@is_login_valid
@validate_registration_details
def create_or_update_user_enquires(request):
    params = json.loads(request.body)
    enquiry_id = params.get('id')
    ward_id = params.get('ward_id')
    params.update({
        "user": request.user,
        "ward": Ward.objects.get(id=ward_id),
        "location_pic": get_file(params.get('location_pic'))
    })
    Enquiry.objects.update_or_create(
        id=enquiry_id,
        defaults=params
    )
    return JsonResponse({
        "validation": 'Enquiry Registered Successfully',
        "status": True
    })


@is_login_valid
def get_states_and_cities(request):
    with open('static/state-city.json') as f:
        data = json.load(f)
        return JsonResponse({
            "data": data,
            "status": True
        })


@is_login_valid
def get_active_wards(request):
    wards = Ward.objects.filter(is_active=True)
    ward_list = [ward.__get_json__() for ward in wards]
    return JsonResponse({
        "status": True,
        "data": ward_list
    })


@is_login_valid
def change_enquiry_status(request):
    params = json.loads(request.body)
    enquiry = Enquiry.objects.get(id=params.get('id'))
    if params.get('comment') and params.get('status_id') in [1, 2]:
        enquiry.comment = params.get('comment')
    
    if params.get('comment_pic'):
        enquiry.comment_pic = get_file(params.get('comment_pic'))

    enquiry.status = params.get('status_id')
    enquiry.save()
    return JsonResponse({
        "status": True,
        "validation": "Status changed successfull"
    })


def get_sensor_data(request):
    params = json.loads(request.body)
    print params
    return JsonResponse({
        "status": True,
        "validation": "Data get successfully"
    })
