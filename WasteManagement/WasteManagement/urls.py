"""WasteManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^is/user/login/$', is_user_logged_in),
    url(r'^user/login/$', auth_view),
    url(r'^user/register/$', register_user),
    url(r'^user/logout/$', logout_view),
    url(r'^user/enquires/$', get_user_enquires),
    url(r'^user/send/otp/$', send_otp_message),
    url(r'^user/forgot/password/$', forgot_password),
    url(r'^create/user/enquiry/$', create_or_update_user_enquires),
    url(r'^get/states/$', get_states_and_cities),
    url(r'^get/active/wards/$', get_active_wards),
    url(r'^change/enquiry/status/$', change_enquiry_status),
    url(r'^get/sensor/data/$', get_sensor_data),
    url(r'^get/sub/wards/$', get_sub_wards),
]
