from django.core.management.base import BaseCommand
from django.utils import timezone
from WasteManagement.models import City, State
import json
from django.db import transaction


class Command(BaseCommand):
    help = 'Update states and cities in models'

    def handle(self, *args, **kwargs):
        obj = {}
        with open('static/state-city.json') as f:
            with open('static/cities_with_pincode.json') as f_pin:
                data = json.load(f)
                f_pin = json.load(f_pin)
                found = 0
                notfound = 0
                for state in data:
                    city_list = []
                    for city in data[state]:
                        try:
                            city_list.append({"pincode": f_pin[city], "city": city})
                            found = found+1
                            print "City -> {} - Pin -> {} - State -> {}".format(
                                city, f_pin[city], state)
                        except:
                            city_list.append({"pincode": 0, "city": city})
                            notfound = notfound+1
                            print "City -> {} No pincode found".format(city)
                    obj[state] = city_list
        with open('data.json', 'a') as the_file:
            the_file.write(json.dumps(obj))

        self.stdout.write("Done")
