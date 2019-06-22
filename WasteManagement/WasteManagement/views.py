import json
from django.contrib import auth
from django.http import JsonResponse
from utils.decorators import is_login_valid, validate_registration_details
from models import Enquiry, Ward
from utils.helper_functions import epoch_to_date, validate_mobile, get_file
from django.contrib.auth.models import User

def user_dict(user):
    return {
        "first_name": user.first_name,
        "last_name": user.last_name
    }


def is_user_logged_in(request):
    print request.session.session_key
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

    if user is not None:
        auth.login(request, user)
        return JsonResponse({
            "validation": "Login Successfull",
            "status": True,
            "user": user_dict(user)
        })
    else:
        return JsonResponse({
            "validation": "User not registered",
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


## Get user enquires
@is_login_valid
def get_user_enquires(requests):
    print requests.user
    dict_obj = json.loads(requests.body)
    date = epoch_to_date(dict_obj.get('date'))
    print date
    kwargs = {}
    kwargs["user__username"] = requests.user.username
    if dict_obj.get('city'):
        kwargs['ward__city__name'] = dict_obj.get('city')

    if dict_obj.get('status'):
        kwargs['status'] = dict_obj.get('status')
    
    if date:
        kwargs['created__day'] = date.day
        kwargs['created__month'] = date.month
        kwargs['created__year'] = date.year
    print kwargs
    enquires = Enquiry.objects.filter(**kwargs)
    enquires = Enquiry.objects.filter(**kwargs)
    enquires_list = []
    for enquiry in enquires:
        enquires_list.append(enquiry.__get_json__())
    
    return JsonResponse({
        "status": True,
        "data": enquires_list
    })


## Get supervisor enquires
@is_login_valid
def get_supervisor_enquires(requests):
    dict_obj = json.loads(requests.body)
    date = epoch_to_date(dict_obj.get('date'))

    kwargs = {}
    kwargs["ward__supervisor__username"] = requests.user
    if dict_obj.get('city'):
        kwargs['ward__city__name'] = dict_obj.get('city')

    if dict_obj.get('user'):
        kwargs['user__username'] = dict_obj.get('user')
    
    if dict_obj.get('status'):
        kwargs['status'] = dict_obj.get('status')
    
    if date:
        kwargs['created__day'] = date.day
        kwargs['created__month'] = date.month
        kwargs['created__year'] = date.year
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
def get_states_and_cities(requests):
    with open('static/state-city.json') as f:
        data = json.load(f)
        return JsonResponse({
            "data": data,
            "status": True
        })

@is_login_valid
def get_active_wards(requests):
    wards = Ward.objects.filter(is_active=True)
    ward_list = [ward.__get_json__() for ward in wards]
    return JsonResponse({
        "status": True,
        "data": ward_list
    })
