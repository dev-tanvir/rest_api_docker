from unittest.mock import patch

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

    # -------------- Test for ChemComps ---------------------

    def test_for_chemcomp_str(self):
        """Test to check chemcomp str representation"""

        checmcomp = models.Chemcomp.objects.create(
            user=sample_user(),
            name="Amino Acid"
        )

        self.assertEqual(str(checmcomp), checmcomp.name)

    # -------------- Test for Synthesize ---------------------

    def test_for_synthesize_str(self):
        """Test to check synthesize str representation"""

        synth = models.Synthesize.objects.create(
            user=sample_user(),
            title="Martian primary life",
            time_years = 10000000,
            chance=54.00

        )

        self.assertEqual(str(synth), synth.title)

    # -------------- Test for Image Upload -------------------

    @patch('uuid.uuid4')
    def test_synthesize_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""

        uuid = '602c7721-2e62-42f7-86da-8920e5cb2653'
        mock_uuid.return_value = uuid
        file_path = models.synthesize_image_file_path(None, 'testImage.jpg')

        expected_path = f'uploads/synthesize/{uuid}.jpg'    #   literal string interpolation (istead of dot notation)
        self.assertEqual(file_path, expected_path)
