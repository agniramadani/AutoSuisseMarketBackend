from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Vehicle, VehicleImage
from django.contrib.auth.models import User
import os, glob


class VehicleViewTests(APITestCase):
    
    """
    Test Vehicle API
    ================
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create a Mercedes-Benz vehicle for testing
        self.vehicle = Vehicle.objects.create(
            owner=self.user,
            make='MERCEDES-BENZ',
            model='C-CLASS',
            year=2022,
            price=35000.00,
            mileage=15000,
            color='Black',
            fuel_type='Petrol',
            transmission='Automatic'
        )

        # Authentication is needed to create the test image, but we must unauthenticate afterward.
        self.client.force_authenticate(user=self.user)
        url = reverse('VehicleImageCreate')
        with open('./media/vehicle_images/test_car.png', 'rb') as img:
            response = self.client.post(url, {'vehicle': self.vehicle.id, 'image': img}, format='multipart')

        self.img_response = response
        self.client.force_authenticate(user=None)

    @classmethod
    def tearDownClass(cls):
        # Delete all images except 'test_img.png' in the specified directory after all tests are done
        image_files = glob.glob("./media/vehicle_images/*.png")
        for file in image_files:
            if not file.endswith("test_car.png"):
                os.remove(file)

    def test_get_all_vehicles(self):
        response = self.client.get(reverse('VehicleList'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_vehicle(self):
        response = self.client.get(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.vehicle.id)

    def test_create_vehicle(self):
        # Create a new vehicle
        data = {
            'make': 'MERCEDES_BENZ',
            'model': 'A-CLASS',
            'year': 2019,
            'price': 22000.00,
            'mileage': 120000,
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
            'model': 'E-CLASS',
            'price': 36000.00,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse('VehicleDetailUpdateDelete', args=[self.vehicle.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.model, 'E-CLASS')
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
            'model': 'A-CLASS',
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


    """
    Test Vehicle Image API
    ======================
    To proceed you need to have /media/vehicle_images/test_car.png
    """

    def test_create_image(self):
        self.client.force_authenticate(user=self.user)
        # Test creating an image
        url = reverse('VehicleImageCreate')
        with open('./media/vehicle_images/test_car.png', 'rb') as img:  # Use a valid image path
            response = self.client.post(url, {'vehicle': self.vehicle.id, 'image': img}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)

    def test_create_image_unauthorized(self):
        # Test creating an image
        url = reverse('VehicleImageCreate')
        with open('./media/vehicle_images/test_car.png', 'rb') as img:  # Use a valid image path
            response = self.client.post(url, {'vehicle': self.vehicle.id, 'image': img}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_image_not_vehicle_owner(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.force_authenticate(user=other_user)
        # Test creating an image
        url = reverse('VehicleImageCreate')
        with open('./media/vehicle_images/test_car.png', 'rb') as img:  # Use a valid image path
            response = self.client.post(url, {'vehicle': self.vehicle.id, 'image': img}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_image(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('VehicleImageDelete', args=[self.img_response.data['id']]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_image_unauthorized(self):
        response = self.client.delete(reverse('VehicleImageDelete', args=[self.img_response.data['id']]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_image_not_vehicle_owner(self):        
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.force_authenticate(user=other_user)

        response = self.client.delete(reverse('VehicleImageDelete', args=[self.img_response.data['id']]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    """
    Test Vehicle Search
    ===================
    """

    def test_get_vehicle_by_make(self):
        response = self.client.get(reverse('SearchVehicle'), {'make': 'MERCEDES-BENZ'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle.id)

    def test_get_vehicle_by_model(self):
        response = self.client.get(reverse('SearchVehicle'), {'model': 'C-CLASS'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle.id)

    def test_get_vehicle_by_year(self):
        response = self.client.get(reverse('SearchVehicle'), {'year': 2022})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle.id)

    def test_get_vehicle_by_price(self):
        response = self.client.get(reverse('SearchVehicle'), {'price': 35000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle.id)

    def test_get_vehicle_no_filters(self):
        response = self.client.get(reverse('SearchVehicle'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.vehicle.id)

    def test_get_all_vehicle_makes(self):
        response = self.client.get(reverse('GetVehicleMakes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_vehicle_models_invalid_make(self):
        response = self.client.get(reverse('GetVehicleModels', kwargs={'requested_make': 'INVALID_MAKE'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_vehicle_models_valid_make(self):
        response = self.client.get(reverse('GetVehicleModels', kwargs={'requested_make': 'MERCEDES-BENZ'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['model'], 'C-CLASS') 
