import random
import os
import requests
from io import BytesIO
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from faker import Faker
from cruises.models import Vessel, Cruise, CruiseStatus, Position, Leg, Scientist, RefList
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate fake data for models'

    def add_arguments(self, parser):
        parser.add_argument('--vessels', type=int, default=5, help='Number of vessels to create')
        parser.add_argument('--cruises', type=int, default=10, help='Number of cruises to create')
        parser.add_argument('--positions', type=int, default=100, help='Number of positions to create')

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Retrieve command-line arguments
        num_vessels = kwargs['vessels']
        num_cruises = kwargs['cruises']
        num_positions = kwargs['positions']

        try:
            # Wrapping the entire process in a transaction to ensure atomicity
            with transaction.atomic():
                # Generate fake users
                users = []
                for _ in range(10):
                    user = User.objects.create_user(
                        username=fake.unique.user_name(),
                        email=fake.unique.email(),
                        password='password'
                    )
                    users.append(user)

                # Generate fake vessels with improved image handling
                vessels = []
                for _ in range(num_vessels):
                    vessel = Vessel.objects.create(
                        vessel_name=fake.unique.company(),
                        vessel_desc=fake.text(),
                        vessel_credit_url=fake.url()
                    )

                    # Handle image download and save
                    try:
                        image_url = fake.image_url(width=800, height=600)
                        response = requests.get(image_url, timeout=10, verify=False)  # Added timeout
                        response.raise_for_status()  # Will raise an HTTPError for bad responses

                        # Validate and save the image file
                        img_name = f"{uuid4()}.jpg"  # Ensure unique filename
                        if response.headers['Content-Type'] in ['image/jpeg', 'image/png']:
                            vessel.vessel_picture.save(img_name, File(BytesIO(response.content)), save=True)
                        else:
                            logger.warning(f"Skipped unsupported image format for URL: {image_url}")

                    except (requests.exceptions.RequestException, ValidationError) as e:
                        logger.error(f"Error downloading or saving image for vessel: {e}")

                    vessels.append(vessel)

                # Generate fake cruise statuses with get_or_create
                statuses = []
                for status_name in ['Scheduled', 'In Progress', 'Completed']:
                    status, created = CruiseStatus.objects.get_or_create(name=status_name)
                    statuses.append(status)

                # Generate fake cruises
                cruises = []
                for _ in range(num_cruises):
                    cruise = Cruise.objects.create(
                        vessel=random.choice(vessels),
                        user=random.choice(users),
                        iso2_country=fake.country_code(),
                        cruise_name=fake.unique.catch_phrase()[:200],
                        cruise_desc=fake.text(),
                        cruise_website_url=fake.url(),
                        cruise_doi_url=fake.url(),
                        cruise_ship_name=fake.word()[:100],
                        cruise_ship_flag=fake.country_code(),
                        cruise_ship_url=fake.url(),
                        cruise_ship_phone_contact=fake.phone_number(),
                        cruise_ship_email_contact=fake.email(),
                        is_multi=fake.boolean(),
                        status=random.choice(statuses)
                    )

                    # Handle image download and save with the same improvements
                    try:
                        image_url = fake.image_url(width=800, height=600)
                        response = requests.get(image_url, timeout=10)
                        response.raise_for_status()

                        # Validate and save the image file
                        img_name = f"{uuid4()}.jpg"  # Ensure unique filename
                        if response.headers['Content-Type'] in ['image/jpeg', 'image/png']:
                            cruise.img_vessel_path.save(img_name, File(BytesIO(response.content)), save=True)
                        else:
                            logger.warning(f"Skipped unsupported image format for URL: {image_url}")

                    except (requests.exceptions.RequestException, ValidationError) as e:
                        logger.error(f"Error downloading or saving image for cruise: {e}")

                    cruises.append(cruise)

                # Generate fake positions using bulk_create for better performance
                positions = []
                for cruise in cruises:
                    for _ in range(num_positions // len(cruises)):
                        positions.append(Position(
                            cruise=cruise,
                            date=fake.date_this_decade(),
                            time=fake.time(),
                            lat=fake.latitude(),
                            lon=fake.longitude()
                        ))
                Position.objects.bulk_create(positions)

                # Generate fake legs with date validation to prevent overlapping
                legs = []
                for cruise in cruises:
                    previous_end_date = None
                    for i in range(random.randint(1, 5)):
                        if previous_end_date:
                            start_date = fake.date_between(start_date=previous_end_date)
                        else:
                            start_date = fake.date_this_year()

                        end_date = fake.date_between(start_date=start_date, end_date='now')
                        previous_end_date = end_date

                        legs.append(Leg(
                            cruise=cruise,
                            leg_number=i + 1,
                            departure_port=fake.city(),
                            return_port=fake.city(),
                            start_date=start_date,
                            end_date=end_date
                        ))
                Leg.objects.bulk_create(legs)

                # Generate fake scientists using bulk_create, without enforcing unique names
                scientists = []
                for cruise in cruises:
                    for _ in range(random.randint(1, 10)):
                        scientists.append(Scientist(
                            cruise=cruise,
                            first_name=fake.first_name(),
                            last_name=fake.last_name(),
                            is_chief_scientist=fake.boolean(),
                            email_contact=fake.unique.email(),  # Unique emails, but not names
                            phone_contact=fake.phone_number()
                        ))
                Scientist.objects.bulk_create(scientists)

                # Generate fake reference lists using bulk_create
                ref_lists = []
                for _ in range(10):
                    ref_lists.append(RefList(
                        list_type=fake.unique.word(),
                        list_desc=fake.sentence()
                    ))
                RefList.objects.bulk_create(ref_lists)

        except Exception as e:
            logger.error(f"Error during fake data generation: {e}")
            self.stdout.write(self.style.ERROR(f'Error during fake data generation: {e}'))

        self.stdout.write(self.style.SUCCESS('Fake data generated successfully!'))
