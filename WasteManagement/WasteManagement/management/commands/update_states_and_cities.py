from django.core.management.base import BaseCommand
from django.utils import timezone
from WasteManagement.models import City, State
import json
from django.db import transaction

class Command(BaseCommand):
    help = 'Update states and cities in models'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                with open('static/cities_state_with_pincode.json') as f:
                    data = json.load(f)
                    for state in data:
                        params = {
                            "name": state
                        }
                        state_qry, created = State.objects.update_or_create(
                            name=state,
                            defaults=params
                        )
                        for city in data[state]:
                            params = {
                                "name": city['city'],
                                "state": state_qry,
                                "pincode": city['pincode']
                            }
                            City.objects.update_or_create(
                                name=state,
                                defaults=params
                            )
                            self.stdout.write("City {} - State {}".format(city, state))
        except Exception as e:
            print e
            self.stdout.write("Exception")
        
        self.stdout.write("Done")