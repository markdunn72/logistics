import datetime
import random

from django.core.management.base import BaseCommand

from faker import Faker
import pytz

from jobs.models import DeliveryJob, Address
from vehicles.models import Vehicle


us_timezones = ['US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific', 'US/Alaska', 'US/Hawaii']
fake = Faker()


class Command(BaseCommand):
    help = "Generates test data for the delivery app"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["create", "destroy"])
        parser.add_argument('--vehicles', type=int, default=2, help="Number of vehicles to create")
        parser.add_argument('--jobs', type=int, default=10, help="Number of delivery jobs to create")


    def handle(self, *args, **options):

        action = options["action"]
        num_vehicles = int(options["vehicles"])
        num_jobs = int(options["jobs"])

        if action == "destroy":
            Vehicle.objects.all().delete()
            Address.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data destroyed."))

        elif action == "create":
            # Create vehicles
            vehicles = [Vehicle(registration=fake.license_plate()) for _ in range(max(1, num_vehicles))]
            Vehicle.objects.bulk_create(vehicles)

            # Create delivery jobs
            for _ in range(max(1, num_jobs)):
                address = Address.objects.create(
                    recipient=fake.name(),
                    street_address=fake.street_address(),
                    street_address_2=fake.secondary_address() if fake.boolean() else '',
                    city=fake.city(),
                    state=fake.state_abbr(),
                    zip_code=fake.zipcode()
                )
                vehicle = random.choice(vehicles)

                (
                    delivery_slot_starts_at,
                    delivery_slot_ends_at,
                    completed_at,
                ) = self.generate_datetimes()

                DeliveryJob.objects.create(
                    vehicle_id=vehicle.registration,
                    destination=address,
                    completed_at=completed_at,
                    income=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
                    cost=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
                    delivery_slot_starts_at=delivery_slot_starts_at,
                    delivery_slot_ends_at=delivery_slot_ends_at,
                )

            self.stdout.write(self.style.SUCCESS(f"Generated {num_vehicles} vehicle objects"))
            self.stdout.write(self.style.SUCCESS(f"Generated {num_jobs} delivery job objects"))

    def generate_datetimes(self):
        timezone_str = random.choice(us_timezones)  # Randomly pick a timezone
        timezone = pytz.timezone(timezone_str)
        now = datetime.datetime.now(timezone)
        max_end_time = now.replace(day=31, month=12)
        start_time = fake.date_time_between_dates(datetime_start=now.replace(day=1, month=1),
                                                  datetime_end=max_end_time).astimezone(timezone)
        end_time = fake.date_time_between_dates(datetime_start=start_time, datetime_end=max_end_time).astimezone(
            timezone)  # Guarantee end time is later
        completed_at = None if fake.boolean() else fake.date_time_between_dates(
            datetime_start=start_time, datetime_end=end_time
        ).astimezone(timezone)  # Half of the jobs are completed during the delivery slot
        return start_time, end_time, completed_at