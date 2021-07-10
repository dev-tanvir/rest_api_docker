from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient # it is a test client

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

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

# ----------------------- Tests for Retreive / Edit ----------------------------

    def test_retrieve_for_user_unauthorized(self):
        """Test to check authentication is required for edit / retrieve"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Testing API endpoints where authentication is required"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='tanvir@gmail.com',
            password="testpass",
            name='Tanvir'
        )

        self.client.force_authenticate(user=self.user) # authenticate user for all tests

    def test_retrieve_profile_success(self):
        """Test that retrieving profile is successful for logged in users"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "name" : self.user.name,
            "email": self.user.email
        })

    def test_retrieve_post_not_allowed(self):
        """Test that post requests are not allowded in me url"""
        response = self.client.post(ME_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test to check authenticated user can update his/her profile"""
        payload = {
            'name': 'tanvir_new',
            'password': 'passwordnew',
        }

        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)