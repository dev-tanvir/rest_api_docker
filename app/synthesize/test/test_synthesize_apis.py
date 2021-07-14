from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Synthesize

from synthesize.serializers import SynthesizeSerializer

SYNTHE_URL = reverse('synthesize:synthesize-list')

def sample_synthesize(user, **params):
    """Create and return an sample synthesizer element"""
    defaults = {
        'title' : 'Sample Synthesizer',
        'time_years' : 500000,
        'chance' : 56,
    }

    defaults.update(params)

    return Synthesize.objects.create(user=user, **defaults)


class SynthesizePublicAPITests(TestCase):
    """This is for synthesize public api tests"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_synthesize_authentication_is_required(self):
        response = self.client.get(SYNTHE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SynthesizePrivateAPITests(TestCase):
    """This is for synthesize private api tests"""
    
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@g.com',
            'testpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_synthesize_authenticated_user(self):
        """Test to check valid users can retrieve synthesizes"""

        sample_synthesize(user=self.user)
        sample_synthesize(user=self.user)

        response = self.client.get(SYNTHE_URL)

        synths = Synthesize.objects.all().order_by('-id')
        serializer = SynthesizeSerializer(synths, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_synthesize_limited_to_authenticated_user(self):
        """Test to check that retrieve synthesizes are all of authenticated user"""

        another_user = get_user_model().objects.create_user(
            'another@gmail.com',
            'testpassanother'
        )
        sample_synthesize(user=another_user, titke="another user")
        synth = sample_synthesize(user=self.user, title="auth user")

        response = self.client.get(SYNTHE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], synth.name)

    

