from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """ Testing user creation"""

    def test_user_creation_email_successful(self):
        """ Testing user creation """

        email = "tanvirfaisaldev@gmail.com"
        password = "123456"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))