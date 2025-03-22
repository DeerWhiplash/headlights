from django.test import TestCase
from django.contrib.auth.models import Group

from myapp.models import UserProfile, Company
from myapp.tests.config import TestData
from myapp.tests.test_Models import TestModels


class TestUserProfile(TestCase):

    def setUp(self):
        TestModels.setUp()
        end_user_group = Group.objects.create(pk=UserProfile.GroupIDs.END_USER_ID, name="end user")
        engineer_group = Group.objects.create(pk=UserProfile.GroupIDs.ENGINEER_ID, name="engineer")
        end_user_group.save()
        engineer_group.save()
    
    def test_validate_unique_username(self):
        #TestModels sets username to TestData.EMAIL, maybe change to TestData.Name?
        result = UserProfile.validate_unique_username(TestData.EMAIL)
        
        self.assertFalse(result.success, "Validation returned successful despite providing a duplicate name")
        
    def test_create_account(self):
        #TestModels sets username to TestData.EMAIL, maybe change to TestData.Name?
        result = UserProfile.create_account(TestData.EMAIL, TestData.EMAIL, TestData.PASSWORD, UserProfile.GroupIDs.ENGINEER_ID)
        self.assertFalse(result.success, "Returned successful despite providing a duplicate name")
        self.assertEqual(result.payload, None)
        
        valid_name = TestData.NAME+"1"
        company = Company.objects.create()
        result = UserProfile.create_account(valid_name, TestData.EMAIL, TestData.PASSWORD, UserProfile.GroupIDs.ENGINEER_ID, company=company)
        groups = list(result.payload.auth_id.groups.values_list('id', flat=True))
        
        self.assertTrue(result.success)
        self.assertTrue(UserProfile.GroupIDs.END_USER_ID in groups, "Created user was not in the end user group")
        self.assertTrue(UserProfile.GroupIDs.ENGINEER_ID in groups, "Created user was not in the engineer group")
