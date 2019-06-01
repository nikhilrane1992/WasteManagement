import json
from django.contrib import auth
from django.http import JsonResponse
from utils.decorators import is_login_valid, validate_registration_details
from models import Enquiry
from utils.helper_functions import epoch_to_date

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
    dict_obj = json.loads(requests.body)
    date = epoch_to_date(dict_obj.get('date'))
    kwargs = {}
    kwargs["user__username"] = requests.user
    if dict_obj.get('city'):
        kwargs['ward__city__name'] = dict_obj.get('city')

    if dict_obj.get('status'):
        kwargs['status'] = dict_obj.get('status')
    
    if date:
        kwargs['created__day'] = date.day
        kwargs['created__month'] = date.month
        kwargs['created__year'] = date.year
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
