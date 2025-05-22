from django.core.management.base import BaseCommand
from apps.models import *

class Command(BaseCommand):
    help = "Delete seeded tenants"

    def handle(self, *args, **kwargs):
        Application.objects.all().delete()
        Lease.objects.all().delete()
        Location.objects.all().delete()
        Manager.objects.all().delete()
        Payment.objects.all().delete()
        Property.objects.all().delete()
        Tenant.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Delete seeded successfully"))
