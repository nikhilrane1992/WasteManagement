from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'A description of your command'

    def handle(self, *args, **options):
        if User.objects.filter(username='optiex').count() < 1:
            User.objects.create_superuser(
                username='optiex',
                email='optiex@optiex.co.in',
                password='optiex@123',
                last_login=timezone.now())
        else:
            print("Super user already present")

        for group in ["CUSTOMER", "ADMIN", "SUPERVISOR"]:
            Group.objects.get_or_create(
                    name = group)
