from django.test import TestCase
from django.contrib.auth.models import Group

from myapp.tests.test_BaseView import BaseViewTest, USER_NAME, USER_PASSWORD
from myapp.tests.config import Views, Templates, TestData
from myapp.models import UserProfile

class AccountCreationTest(BaseViewTest, TestCase):

    URL = Views.ACCOUNT_CREATION
    TEMPLATE = Templates.ACCOUNT_CREATION

    def setUp(self):
        end_user_group = Group.objects.create(pk=UserProfile.GroupIDs.END_USER_ID, name="end user")
        finance_group = Group.objects.create(pk=UserProfile.GroupIDs.FINANCE_ID, name="finance")
        engineer_group = Group.objects.create(pk=UserProfile.GroupIDs.ENGINEER_ID, name="engineer")
        end_user_group.save()
        finance_group.save()
        engineer_group.save()
        
        return BaseViewTest.setUp(self)

    def test_get_view(self):
        self.client.login(username=USER_NAME, password=USER_PASSWORD)
        BaseViewTest.test_get_view(self)
        
        self.client.logout()
        BaseViewTest.test_get_view(self)
        
    def test_account_creation(self):
        #If the user is logged in they are redirected to the home page
        self.client.login(username=USER_NAME, password=USER_PASSWORD)
        response = BaseViewTest._test_post_view_response(self)
        self.assertEqual(response.templates[0].name, Templates.HOME)
        self.client.logout()
        
        #This should successfully create an account, logging in the user and redirecting them to the home page
        unique_name = TestData.NAME+"ACCOUNT_CREATION_TEST"
        payload = {"username": unique_name, "email": TestData.EMAIL, "password": TestData.PASSWORD, "userType": UserProfile.GroupIDs.FINANCE_ID, "isOwner": True}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        self.assertEqual(response.templates[0].name, Templates.HOME)
        self.client.logout()
        
        #Unique_name has already been used at this point, prompting an error
        payload = {"username": unique_name, "email": TestData.EMAIL, "password": TestData.PASSWORD, "userType": UserProfile.GroupIDs.END_USER_ID}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        self.assertEqual(response.templates[0].name, Templates.ACCOUNT_CREATION)
        response_context = response.context.pop()
        print(response_context)
        self.assertEqual(len(response_context['error_messages']), 1)

        #Creating an AI engineer account will default to is_active=false, returns to home
        unique_engineer = TestData.NAME+"ENGINEER_TEST"
        payload = {"username": unique_engineer, "email": TestData.EMAIL, "password": TestData.PASSWORD, "userType": UserProfile.GroupIDs.ENGINEER_ID}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        self.assertEqual(response.templates[0].name, Templates.HOME)
        self.client.logout()
