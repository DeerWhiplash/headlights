from django.test import TestCase
from django.contrib.auth.models import User
from myapp.forms.CustomAuthenticationForm import CustomAuthenticationForm
from django.contrib.auth import authenticate

class CustomAuthenticationFormTest(TestCase):

    def setUp(self):
        # Create a user with inactive status
        self.inactive_user = User.objects.create_user(username="inactiveuser", password="testpassword")
        self.inactive_user.is_active = False
        self.inactive_user.save()

        # Create a user with active status
        self.active_user = User.objects.create_user(username="activeuser", password="testpassword")
        self.active_user.is_active = True
        self.active_user.save()

    def test_inactive_user_login(self):
        # Test that the form raises an error for inactive users
        form_data = {
            'username': 'inactiveuser',
            'password': 'testpassword',
        }
        form = CustomAuthenticationForm(data=form_data)

        # Check if the form is not valid
        self.assertFalse(form.is_valid())
        
        # Ensure the error message is specific to inactive users
        self.assertEqual(form.errors['__all__'][0], 'Your account is inactive. Please contact support.')

    def test_active_user_login(self):
        # Test that the form works for an active user
        form_data = {
            'username': 'activeuser',
            'password': 'testpassword',
        }
        form = CustomAuthenticationForm(data=form_data)

        # Check if the form is valid
        self.assertTrue(form.is_valid())

        user = authenticate(username='activeuser', password='testpassword')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_active)

    def tearDown(self):
        # Clean up users after tests
        self.inactive_user.delete()
        self.active_user.delete()
