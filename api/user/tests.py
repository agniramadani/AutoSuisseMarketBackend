from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse


class UserTests(APITestCase):

    def setUp(self):
        # Create two users for testing
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.client = APIClient()

    def test_get_all_users(self):
        # Authenticate and request all users
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('UserList'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_single_user(self):
        # Authenticate and request single user (user1)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('UserDetailUpdateDelete', args=[self.user1.pk]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user1.pk)

    def test_update_user(self):
        # Authenticate as user1 and update user1's data
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(reverse('UserDetailUpdateDelete', args=[self.user1.pk]), 
                                    {'username': 'updated_user1'}, 
                                    format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'updated_user1')

    def test_update_user_not_owner(self):
        # Authenticate as user2 and try to update user1's data (should fail)
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(reverse('UserDetailUpdateDelete', args=[self.user1.pk]), 
                                    {'username': 'fail_update'}, 
                                    format='json')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_user(self):
        # Authenticate as user1 and delete user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('UserDetailUpdateDelete', args=[self.user1.pk]))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_not_owner(self):
        # Authenticate as user2 and try to delete user1 (should fail)
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(reverse('UserDetailUpdateDelete', args=[self.user1.pk]))
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AuthenticationTests(APITestCase):

    def setUp(self):
        # Create a user in the test db
        self.user_data = {'username': 'testuser', 'password': 'password123'}
        self.user = User.objects.create_user(**self.user_data)
        # This will be used to test login and signup missing credentials
        self.test_cases = [
            {'password': 'newpassword123'},
            {'username': 'newuser'},
            {},
        ]

    def test_login_user(self):
        # Login with the user from test db
        response = self.client.post(reverse('Login'), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_missing_credentials(self):
        # Test login with missing username or password
        for data in self.test_cases:
            response = self.client.post(reverse('Login'), data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_credentials(self):
        # Test login with an invalid password
        response = self.client.post(reverse('Login'), {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_signup_user(self):
        # Signup with a new user 
        _new_user = {'username': 'newuser', 'password': 'newpassword123'}
        response = self.client.post(reverse('Signup'), _new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_signup_missing_credentials(self):
        # Test signup with missing username or password
        for data in self.test_cases:
            response = self.client.post(reverse('Signup'), data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
