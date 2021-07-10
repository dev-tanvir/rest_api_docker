from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from synthesize.serializers import TagSerializer

TAG_URL = reverse('synthesize:tag-list') # viewSet


class PublicTagAPITests(TestCase):
    """The public API tests for tag model"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_tag_api_login_required(self):
        """Test to check retrieving tag api requires login"""
        response = self.client.get(TAG_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Tests that require authentication"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'tanvir@g.com',
            'testpass',
        )

        self.client.force_authenticate(user=self.user)

    def test_retrieve_tag_authenticated_user(self):
        """Test to check valid users can retrieve tags"""

        Tag.objects.create(name='Venus', user=self.user)
        Tag.objects.create(name='Saturn', user=self.user)

        response = self.client.get(TAG_URL) # from API

        tags = Tag.objects.all().order_by('-name') # from db - ordered by
        serializer = TagSerializer(tags, many=True) # db object to json

        print(tags)
        print(type(tags), "ser ===> ", type(serializer))
        print(serializer)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        print(serializer.data)
        self.assertEqual(response.data, serializer.data)    # comparing API result and query result

    def test_tags_limited_to_authenticated_user(self):
        """Test to check that retrieve tags are all of authenticated user"""

        another_user = get_user_model().objects.create_user(
            'another@gmail.com',
            'testpassanother'
        )
        Tag.objects.create(user=another_user, name="Mars")
        tag = Tag.objects.create(user=self.user, name="Earth")

        response = self.client.get(TAG_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # it should return only 1 data i.e. Earth - for authenticated user
        self.assertEqual(response.data[0]['name'], tag.name)



