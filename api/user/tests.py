from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


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
