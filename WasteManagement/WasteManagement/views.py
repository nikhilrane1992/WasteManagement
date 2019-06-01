import json
from django.contrib import auth
from django.http import JsonResponse
from utils.decorators import is_login_valid, validate_registration_details
from models import Enquiry

def auth_view(request):
    dict = json.loads(request.body)

    username = dict['username']
    password = dict['password']

    print username, password

    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
    return JsonResponse({
        "validation": "Login Successfull",
        "status": True
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
    enquires = Enquiry.objects.filter(user__username = requests.user)
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
    print requests.user
    enquires = Enquiry.objects.filter(ward__supervisor__username = requests.user)
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
    params.update({
        "user": request.user
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
