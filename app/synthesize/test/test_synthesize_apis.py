import os
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Synthesize, Tag, Chemcomp

from synthesize.serializers import SynthesizeSerializer, SynthesizeDetailSerializer

SYNTHE_URL = reverse('synthesize:synthesize-list')

def image_upload_url(synthe_id):
    return reverse('synthesize:synthesize-upload-image', args=[synthe_id])

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

    # ------------- Test Synthesize Create ---------------------------

    def test_create_basic_synthesize(self):
        payload = {
            'title' : 'Sample title',
            'time_years' : 500000,
            'chance' : 69,
        }

        res = self.client.post(SYNTHE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        synthe = Synthesize.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(synthe, key))

    def test_create_synthesize_with_tags(self):
        tag_1 = sample_tag(user=self.user, name="Tag 1")
        tag_2 = sample_tag(user=self.user, name="Tag 2")

        payload = {
            'title' : 'Sample title',
            'time_years' : 500000,
            'chance' : 69,
            'tags' : [tag_1.id, tag_2.id],
        }

        res = self.client.post(SYNTHE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        synthe = Synthesize.objects.get(id=res.data['id'])
        tags = synthe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag_1, tags)
        self.assertIn(tag_2, tags)

    def test_create_synthesize_with_chemcomps(self):
        cc_1 = sample_chemcomp(user=self.user, name="CC 1")
        cc_2 = sample_chemcomp(user=self.user, name="CC 2")

        payload = {
            'title' : 'Sample title',
            'time_years' : 500000,
            'chance' : 69,
            'chemcomps' : [cc_1.id, cc_2.id],
        }

        res = self.client.post(SYNTHE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        synthe = Synthesize.objects.get(id=res.data['id'])
        ccs = synthe.chemcomps.all()
        self.assertEqual(len(ccs), 2)
        self.assertIn(cc_1, ccs)
        self.assertIn(cc_2, ccs)

    # -------------- Test update Synthesize ----------------------

    def test_partial_update_synthesize(self):
        """Test to partally update synthesize object using patch"""
        synthe = sample_synthesize(user=self.user)
        synthe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="New Tag")

        payload = {
            'title' : 'Updated Title',
            'tags' : [new_tag.id],
        }

        url = detail_url(synthe.id)
        self.client.patch(url, payload)

        synthe.refresh_from_db()

        # after updating
        self.assertEqual(synthe.title, payload['title'])
        tags = synthe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_synthesize(self):
        """Test to fully update synthesize object using put"""
        synthe = sample_synthesize(user=self.user)
        synthe.tags.add(sample_tag(user=self.user))

        payload = {
            'title' : 'Updated Title',
            'chance' : Decimal('60.05'),    # to pass assertEqual, use 60.00 or Decimal('60.05') as 60.05 is float and not exact i.e. 60.050000000001
            'time_years' : 7896590
        }

        url = detail_url(synthe.id)
        self.client.put(url, payload)

        synthe.refresh_from_db()

        # after updating
        self.assertEqual(synthe.title, payload['title'])
        # print(type(synthe.chance))
        # print(type(payload['chance']))
        self.assertEqual(synthe.chance, payload['chance'])
        self.assertEqual(synthe.time_years, payload['time_years'])

        tags = synthe.tags.all()
        self.assertEqual(len(tags), 0)


class SynthesizeImageUploadAPITests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@g.com',
            'testpass'
        )
        self.client.force_authenticate(user=self.user)
        self.synthe = sample_synthesize(user=self.user)

    def tearDown(self) -> None:
        self.synthe.image.delete()  #   to keep the file systems clean from unnecessary test temp files

    def test_upload_image_to_synthesize(self):
        """Test to check valid image file upload is successful"""
        url = image_upload_url(self.synthe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf: # we are opening named file cause we need filename to uuid
            img_data = Image.new('RGB', (10, 10))   #   creating an image data
            img_data.save(ntf, format="JPEG")   #   writing that image data to the file
            ntf.seek(0)                         #   after writing, we point to the start of the file again
            res = self.client.post(url, {'image':ntf}, format='multipart')
                                                #   format='multipart' is to tell that this post request not only has json but also data

        self.synthe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.synthe.image.path)) #   it will not get path from image if db is not refreshed

    def test_upload_invalid_image_to_synthesize(self):
        """Test to check invalid image file upload is unsuccessful"""
        url = image_upload_url(self.synthe.id)
        res = self.client.post(url, {'image': 'invalid image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)