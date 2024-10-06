from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Vehicle
from django.contrib.auth.models import User


class VehicleViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create a Mercedes-Benz vehicle for testing
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make='Mercedes-Benz',
            model='C-Class',
            year=2022,
            price=35000.00,
            mileage=15000,
            color='Black',
            fuel_type='Petrol',
            transmission='Automatic'
        )

    def test_get_all_vehicles(self):
        response = self.client.get(reverse('VehicleList'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_vehicle(self):
        response = self.client.get(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.vehicle.id)

    def test_create_vehicle(self):
        data = {
            'make': 'Honda',
            'model': 'Civic',
            'year': 2021,
            'price': 22000.00,
            'mileage': 12000,
            'color': 'Blue',
            'fuel_type': 'Petrol',
            'transmission': 'Manual'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('VehicleList'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehicle.objects.count(), 2)

    def test_update_vehicle(self):
        data = {
            'model': 'E-Class',
            'price': 36000.00,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.model, 'E-Class')
        self.assertEqual(self.vehicle.price, 36000.00)

    def test_update_vehicle_owner(self):
        data = {
            'owner': 123,  # Attempting to change the owner
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_vehicle_not_owner(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.force_authenticate(user=other_user)
        
        data = {
            'model': 'A-Class',
        }
        response = self.client.put(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]), data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_vehicle(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vehicle.objects.count(), 0)

    def test_delete_vehicle_not_owner(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.force_authenticate(user=other_user)
        
        response = self.client.delete(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
