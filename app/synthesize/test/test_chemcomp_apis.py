from django.contrib.auth import get_user_model
from django.http import response
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Chemcomp
from synthesize.serializers import ChemcompSerializer

CHEMCOMP_URL = reverse("synthesize:chemcomp-list")


class ChemcompPublicAPITests(TestCase):
    """The public API tests for chemcomp model"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_chemcomp_api_login_required(self):
        """Test to check retrieving chemcomp api requires login"""
        response = self.client.get(CHEMCOMP_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChemcompPrivateAPITests(TestCase):
    """The private API tests for chemcomp model"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "tanvir@g.com",
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_chemcomp_authenticated_user(self):
        """Test to check valid users can retrieve chemcomps"""
        Chemcomp.objects.create(name="Amino Acid", user=self.user)
        Chemcomp.objects.create(name="Water", user=self.user)

        response = self.client.get(CHEMCOMP_URL)

        chemcomps = Chemcomp.objects.all().order_by('-name')
        serializer = ChemcompSerializer(chemcomps, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_chemcomps_limited_to_authenticated_user(self):
        """Test to check that retrieve chemcomps are all of authenticated user"""
        user2 = get_user_model().objects.create_user(
            'user2@g.com',
            'testpassuser2'
        )

        auth_user_chemcomp = Chemcomp.objects.create(name="Amino Acid", user=self.user)
        Chemcomp.objects.create(name="Water", user=user2)
        
        response = self.client.get(CHEMCOMP_URL)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], auth_user_chemcomp.name)

    # ----------------- Test create Chemcomp -------------------

    def test_create_chemcomp_successful(self):
        """Test to check creation of chemcomp is successful"""
        payload ={
            'name' : 'Methane gas',
        }

        self.client.post(CHEMCOMP_URL, payload)

        tag_exists = Chemcomp.objects.filter(user=self.user,name=payload['name']).exists()
        self.assertTrue(tag_exists)

    def test_create_chemcomp_invalid(self):
        """Test to check invalid chemcomp is not created"""
        payload ={
            'name' : '',
        }

        response = self.client.post(CHEMCOMP_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

