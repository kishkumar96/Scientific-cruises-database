import csv
from faker import Faker
import uuid
from datetime import datetime

fake = Faker()

def generate_fake_data():
    generate_fake_vessel_data('fake_vessels.csv', 100)
    generate_fake_cruise_status_data('fake_cruise_status.csv', 10)
    generate_fake_cruise_data('fake_cruises.csv', 50)
    generate_fake_position_data('fake_positions.csv', 500)

def generate_fake_vessel_data(filename, num_records):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'vessel_id', 'vessel_name', 'vessel_desc', 'vessel_picture', 'vessel_credit_url'
        ])

        for _ in range(num_records):
            vessel_id = uuid.uuid4()
            vessel_name = fake.company()
            vessel_desc = fake.text()
            vessel_picture = ''
            vessel_credit_url = fake.url()
            
            writer.writerow([
                vessel_id, vessel_name, vessel_desc, vessel_picture, vessel_credit_url
            ])

def generate_fake_cruise_status_data(filename, num_records):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['name'])

        for _ in range(num_records):
            name = fake.word()
            writer.writerow([name])

def generate_fake_cruise_data(filename, num_records):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'cruise_id', 'vessel_id', 'user_id', 'iso2_country', 'cruise_name', 'cruise_desc', 
            'cruise_website_url', 'cruise_doi_url', 'cruise_ship_name', 'cruise_ship_flag', 
            'cruise_ship_url', 'cruise_ship_phone_contact', 'cruise_ship_email_contact', 
            'is_multi', 'img_vessel_path', 'status_id'
        ])

        for _ in range(num_records):
            cruise_id = uuid.uuid4()
            vessel_id = uuid.uuid4()  # Replace with actual vessel IDs
            user_id = 1  # Replace with actual user IDs
            iso2_country = fake.country_code()
            cruise_name = fake.sentence(nb_words=4)
            cruise_desc = fake.text()
            cruise_website_url = fake.url()
            cruise_doi_url = fake.url()
            cruise_ship_name = fake.company()
            cruise_ship_flag = fake.country_code()
            cruise_ship_url = fake.url()
            cruise_ship_phone_contact = fake.phone_number()
            cruise_ship_email_contact = fake.email()
            is_multi = fake.boolean()
            img_vessel_path = ''
            status_id = 1  # Replace with actual status IDs
            
            writer.writerow([
                cruise_id, vessel_id, user_id, iso2_country, cruise_name, cruise_desc, 
                cruise_website_url, cruise_doi_url, cruise_ship_name, cruise_ship_flag, 
                cruise_ship_url, cruise_ship_phone_contact, cruise_ship_email_contact, 
                is_multi, img_vessel_path, status_id
            ])

def generate_fake_position_data(filename, num_records):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            'position_id', 'cruise_id', 'date', 'time', 'lat', 'lon', 'coordinates'
        ])

        for _ in range(num_records):
            position_id = uuid.uuid4()
            cruise_id = uuid.uuid4()  # Replace with actual cruise IDs
            date = fake.date_this_year()
            time = fake.time()
            lat = fake.latitude()
            lon = fake.longitude()
            coordinates = f'POINT({lon} {lat})'
            
            writer.writerow([
                position_id, cruise_id, date, time, lat, lon, coordinates
            ])

# Generate fake data
generate_fake_data()
