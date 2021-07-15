from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Synthesize, Tag, Chemcomp

from synthesize.serializers import SynthesizeSerializer, SynthesizeDetailSerializer

SYNTHE_URL = reverse('synthesize:synthesize-list')

def detail_url(synthe_id):
    return reverse('synthesize:synthesize-detail', args=[synthe_id])

def sample_synthesize(user, **params):
    """Create and return an sample synthesizer element"""
    defaults = {
        'title' : 'Sample Synthesizer',
        'time_years' : 500000,
        'chance' : 56,
    }

    defaults.update(params)

    return Synthesize.objects.create(user=user, **defaults)

def sample_tag(user, name="Sample Tag"):
    return Tag.objects.create(name=name, user=user)

def sample_chemcomp(user, name="Sample Chempcomp"):
    return Chemcomp.objects.create(name=name, user=user)


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
        sample_synthesize(user=another_user, title="another user")
        synth = sample_synthesize(user=self.user, title="auth user")

        response = self.client.get(SYNTHE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], synth.title)

    # ------------- Test Synthesize detail --------------------------

    def test_view_synthesize_detail(self):
        """Test to check detail view of synthesize objects"""
        synthe = sample_synthesize(user=self.user)
        synthe.tags.add(sample_tag(user=self.user))
        synthe.chemcomps.add(sample_chemcomp(self.user))

        res = self.client.get(detail_url(synthe.id))
        serializer = SynthesizeDetailSerializer(synthe)    

        self.assertEqual(res.data, serializer.data)

