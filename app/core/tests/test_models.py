from django.test import TestCase
from django.contrib.auth import get_user_model


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