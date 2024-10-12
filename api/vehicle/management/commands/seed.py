import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vehicle.models import Vehicle, VehicleImage
from django.core.files import File

class Command(BaseCommand):
    help = 'Seed the database with fake users, vehicles, and images'

    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))    

    def handle(self, *args, **kwargs):
        # Create Users
        user1 = User.objects.create_user(
            username='anna_müller', password='password1',
            first_name='Anna', last_name='Müller', email='anna.mueller@fake.ch'
        )
        user2 = User.objects.create_user(
            username='lucas_meier', password='password2',
            first_name='Lucas', last_name='Meier', email='lucas.meier@fake.ch'
        )
        user3 = User.objects.create_user(
            username='sophie_bernhard', password='password3',
            first_name='Sophie', last_name='Bernhard', email='sophie.bernhard@fake.ch'
        )
        user4 = User.objects.create_user(
            username='nicolas_schneider', password='password4',
            first_name='Nicolas', last_name='Schneider', email='nicolas.schneider@fake.ch'
        )

        # Seed Vehicles
        vehicles_data = [
            {'owner': user1, 'make': 'TOYOTA', 'model': 'CAMRY', 'year': 2015, 'price': 12000, 'mileage': 80000, 'color': 'Red', 'fuel_type': 'Petrol', 'transmission': 'Automatic'},
            {'owner': user4, 'make': 'TOYOTA', 'model': 'COROLLA', 'year': 2020, 'price': 18000, 'mileage': 30000, 'color': 'Blue', 'fuel_type': 'Hybrid', 'transmission': 'Manual'},
            {'owner': user2, 'make': 'HONDA', 'model': 'CIVIC', 'year': 2018, 'price': 14000, 'mileage': 60000, 'color': 'Blue', 'fuel_type': 'Petrol', 'transmission': 'Manual'},
            {'owner': user3, 'make': 'TESLA', 'model': 'MODEL S', 'year': 2020, 'price': 60000, 'mileage': 20000, 'color': 'Black', 'fuel_type': 'Electric', 'transmission': 'Automatic'},
            
            {'owner': user3, 'make': 'MERCEDES-BENZ', 'model': 'C-CLASS', 'year': 2018, 'price': 25000, 'mileage': 45000, 'color': 'Black', 'fuel_type': 'Diesel', 'transmission': 'Automatic'},
            {'owner': user1, 'make': 'MERCEDES-BENZ', 'model': 'E-CLASS', 'year': 2021, 'price': 45000, 'mileage': 15000, 'color': 'White', 'fuel_type': 'Petrol', 'transmission': 'Automatic'},
            
            {'owner': user2, 'make': 'BMW', 'model': '3 SERIES', 'year': 2019, 'price': 35000, 'mileage': 38000, 'color': 'Grey', 'fuel_type': 'Petrol', 'transmission': 'Automatic'},
            
            {'owner': user4, 'make': 'VOLKSWAGEN', 'model': 'GOLF 7', 'year': 2017, 'price': 20000, 'mileage': 50000, 'color': 'White', 'fuel_type': 'Petrol', 'transmission': 'Manual'},
            {'owner': user3, 'make': 'VOLKSWAGEN', 'model': 'GOLF 8', 'year': 2021, 'price': 32000, 'mileage': 15000, 'color': 'Blue', 'fuel_type': 'Hybrid', 'transmission': 'Automatic'},
            
            {'owner': user4, 'make': 'AUDI', 'model': 'A4', 'year': 2016, 'price': 28000, 'mileage': 60000, 'color': 'Silver', 'fuel_type': 'Diesel', 'transmission': 'Manual'},
        ]

        for data in vehicles_data:
            vehicle = Vehicle.objects.create(**data)
            self.stdout.write(f"Created {vehicle}")

            # Add images to vehicles from folder
            image_folder = f'./seed_cars/{data["make"]}/{data["model"]}'
            if os.path.exists(image_folder):
                for img_file in os.listdir(image_folder):
                    with open(f"{image_folder}/{img_file}", 'rb') as f:
                        VehicleImage.objects.create(vehicle=vehicle, image=File(f))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
