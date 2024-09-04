import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Vessel, CruiseStatus, Cruise, Position, Leg, Scientist
from django.utils import timezone
from uuid import uuid4

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake data for testing'

    def handle(self, *args, **kwargs):
        self.generate_users(10)
        self.generate_vessels(5)
        self.generate_cruise_statuses()
        self.generate_cruises(20)
        self.generate_positions(100)
        self.generate_legs(30)
        self.generate_scientists(50)

    def generate_users(self, count):
        for _ in range(count):
            User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123'
            )
        self.stdout.write(self.style.SUCCESS(f'Generated {count} users'))

    def generate_vessels(self, count):
        for _ in range(count):
            Vessel.objects.create(
                vessel_id=uuid4(),
                vessel_name=fake.company(),
                vessel_desc=fake.text(),
                vessel_picture=None,
                vessel_credit_url=fake.url()
            )
        self.stdout.write(self.style.SUCCESS(f'Generated {count} vessels'))

    def generate_cruise_statuses(self):
        statuses = ['Planned', 'In Progress', 'Completed', 'Cancelled']
        for status in statuses:
            CruiseStatus.objects.create(name=status)
        self.stdout.write(self.style.SUCCESS('Generated cruise statuses'))

    def generate_cruises(self, count):
        vessels = list(Vessel.objects.all())
        users = list(User.objects.all())
        statuses = list(CruiseStatus.objects.all())

        for _ in range(count):
            cruise = Cruise.objects.create(
                cruise_id=uuid4(),
                vessel=random.choice(vessels),
                user=random.choice(users),
                iso2_country=fake.country_code(),
                cruise_name=fake.sentence(nb_words=4),
                cruise_desc=fake.text(),
                cruise_website_url=fake.url(),
                cruise_doi_url=fake.url(),
                cruise_ship_name=fake.company(),
                cruise_ship_flag=fake.country_code(),
                cruise_ship_url=fake.url(),
                cruise_ship_phone_contact=fake.phone_number(),
                cruise_ship_email_contact=fake.email(),
                is_multi=fake.boolean(),
                img_vessel_path=None,
                status=random.choice(statuses)
            )
        self.stdout.write(self.style.SUCCESS(f'Generated {count} cruises'))

    def generate_positions(self, count):
        cruises = list(Cruise.objects.all())

        for _ in range(count):
            cruise = random.choice(cruises)
            Position.objects.create(
                position_id=uuid4(),
                cruise=cruise,
                date=fake.date_this_year(),
                time=fake.time(),
                lat=fake.latitude(),
                lon=fake.longitude()
            )
        self.stdout.write(self.style.SUCCESS(f'Generated {count} positions'))

    def generate_legs(self, count):
        cruises = list(Cruise.objects.all())

        for _ in range(count):
            Leg.objects.create(
                leg_id=uuid4(),
                cruise=random.choice(cruises),
                leg_number=fake.random_int(min=1, max=10),
                departure_port=fake.city(),
                return_port=fake.city(),
                start_date=fake.date_this_year(),
                end_date=fake.date_this_year()
            )
        self.stdout.write(self.style.SUCCESS(f'Generated {count} legs'))

    def generate_scientists(self, count):
        cruises = list(Cruise.objects.all())

        for _ in range(count):
            Scientist.objects.create(
                scientist_id=uuid4(),
                cruise=random.choice(cruises),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_chief_scientist=fake.boolean(),
                email_contact=fake.email(),
                phone_contact=fake.phone_number()
            )
        self.stdout.write(self.style.SUCCESS(f'Generated {count} scientists'))
