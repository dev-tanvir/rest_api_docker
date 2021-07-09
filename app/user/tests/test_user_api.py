from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient # it is a test client

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

#helper functions for API testing
def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_user_create_valid_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'tanvir@g.com',
            'password': 'testpass',
            'name': 'Tanvir Faisal'
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data) # check - password is not returned in response

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'tanvir@g.com',
            'password': 'testpass',
            'name': 'Tanvir Faisal',
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test password must be more than 5 characters"""

        payload = {
            'email': 'tanvir@g.com',
            'password': 'pw',
            'name': 'Tanvir Faisal',
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # NOw testing if a user is really not created
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()

        self.assertFalse(user_exists)

    # ----------------------- Tests for Token ----------------------------

    def test_create_token_for_user(self):
        """Test to check if a token is created for user"""
        payload = {
            'email': 'tanvir@g.com',
            'password': 'testpass',
        }

        create_user(**payload)

        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test to check create token when invalid credentials is given"""

        create_user(email='tanvir@g.com',password='testpass',name='Tanvir Faisal')
        payload = {
            'email': 'tanvir@g.com',
            'password': 'oopsworng',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_no_user(self):
        """Test to check create token when there is no user"""
        payload = {
            'email': 'tanvir@g.com',
            'password': 'testpass',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_missing_credentials(self):
        """Test to check when required credentials are missing"""
        payload = {
            'email': 'tanvir@g.com',
            'password': '',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)