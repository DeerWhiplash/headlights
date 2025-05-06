from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now


import logging
from unittest.mock import patch

from myapp.tests.test_BaseView import BaseViewTest
from myapp.tests.config import Views, Templates, TestData
from myapp.models import UserProfile, Company, FinanceReport

class FinanceDashboardTest(BaseViewTest, TestCase):

    URL = Views.FINANCE_DASHBOARD
    TEMPLATE = Templates.FINANCE

    def setUp(self):
        logging.disable(logging.ERROR)

        end_user_group = Group.objects.create(pk=UserProfile.GroupIDs.END_USER_ID, name="end user")
        end_user_group.save()
        
        finance_group = Group.objects.create(pk=UserProfile.GroupIDs.FINANCE_ID, name="finance")
        finance_permission = Permission.objects.get(codename="view_financereport")
        finance_group.permissions.add(finance_permission)
        finance_group.save()
        
        BaseViewTest.setUp(self)

        self.client.logout()
        self.TEMPLATE = Templates.LOGIN
        BaseViewTest.test_get_view(self)
        
        unique_name = TestData.NAME+"FINANCE_DASHBOARD_SETUP"
        company = Company.objects.get(company_id=1)
        UserProfile.create_account(unique_name, TestData.EMAIL, TestData.PASSWORD, UserProfile.GroupIDs.FINANCE_ID, company=company)
        self.client.login(username=unique_name, password=TestData.PASSWORD)
        self.TEMPLATE = Templates.FINANCE

    def test_get_view(self):
        BaseViewTest.test_get_view(self)

        # Create superuser to hit superuser logic for invoices viewing.
        User = get_user_model()
        auth_id = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='superpassword'
        )
        UserProfile.objects.create(auth_id=auth_id)

        self.client.login(username='admin', password='superpassword')
        BaseViewTest.test_get_view(self)
        
        # Create individual user to hit non-company user logic for viewing invoices.
        unique_name = TestData.NAME+"FINANCE_DASHBOARD_GET_VIEW_TEST"
        new_user = UserProfile.create_account(unique_name, TestData.EMAIL, TestData.PASSWORD, UserProfile.GroupIDs.FINANCE_ID, company=None).payload

        time_now = now()

        # Create invoice with zero value CostIncurred and one with proper CostIncurred to hit PayPal logic.
        zero_invoice = FinanceReport.objects.create(
            cost_incurred=0,
            created_at=time_now,
            user_profile_id=new_user,
            paid=False
        )

        FinanceReport.objects.create(
            cost_incurred=100,
            created_at=time_now,
            user_profile_id=new_user,
            paid=False
        )
        
        self.client.login(username=unique_name, password=TestData.PASSWORD)
        BaseViewTest.test_get_view(self)

        zero_invoice.refresh_from_db()
        self.assertTrue(zero_invoice.paid)

    def test_company_post_view_success(self):
        payload = {
            'invoice_type': 'company',
            'entity': 1,
            'month': '4',
            'year': '2025',
        }

        BaseViewTest._test_post_view_response(self, payload=payload)

    def test_individual_post_view_success(self):
        user_profile = UserProfile.objects.filter(user_profile_id=1).first()
        user_profile.company_id = None
        user_profile.is_company_owner = False
        user_profile.save()

        payload = {
            'invoice_type': 'individual',
            'entity': 1,
            'month': '4',
            'year': '2025',
        }

        BaseViewTest._test_post_view_response(self, payload=payload)

    def test_post_view_failure_no_content(self):
        BaseViewTest._test_post_view_response(self, status=400)

    @patch("myapp.views.FinanceDashboardViews.generate_invoice")
    def test_generate_invoice_exception(self, mock_generate_invoice):
        mock_generate_invoice.side_effect = Exception("Simulated failure")

        payload= {
            'invoice_type': 'company',
            'entity': 1,
            'month': '4',
            'year': '2025',
        }

        response = BaseViewTest._test_post_view_response(self, status=500, payload=payload)
        self.assertIn("An exception occurred", response.content.decode())

    def test_invoice_download_success(self):
        response = self.client.get(reverse('invoice_download', args=[1]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename=invoice_1.pdf', response['Content-Disposition'])

        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_invoice_download_failure(self):
        response = self.client.get(reverse('invoice_download', args=[999]))

        self.assertContains(response, 'Failed to download invoice', status_code=400)

    def test_load_entity_field(self):
        response = self.client.get(reverse('load_entity_field'))
        self.assertEqual(response.status_code, 200)
