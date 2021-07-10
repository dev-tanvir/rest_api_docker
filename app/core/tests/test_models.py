from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email="tanvir@g.com",password="testpass"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """ Testing user creation"""

    def test_user_creation_email_successful(self):
        """ Testing user creation with email"""

        email = "tanvirfaisaldev@gmail.com"
        password = "123456"

        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password)) # comes with django user model - as password is encrypted 

    def test_new_user_email_normalization(self):
        """Testing new user email normalization"""

        email = "tanvirfaisaldev@GMAIL.COM"

        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_email_validated(self):
        with self.assertRaises(ValueError): # it tests if following condition raises valueerror, if not test fails
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Testing creating new super user"""

        user = get_user_model().objects.create_superuser('test@test.com', '123456')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # --------------- Test for tags -------------------------

    def test_tag_str_representation(self):
        """Test to check tag representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Martian"
        )

        self.assertEqual(str(tag), tag.name)