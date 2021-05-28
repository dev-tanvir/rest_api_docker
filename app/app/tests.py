from django.test import TestCase
from app.calc import add

class DjangoTest(TestCase):

    def test_add(self):
        self.assertEqual(add(3,8), 11)