from django.contrib.auth.models import User, Group, Permission
from django.test import Client, TestCase
from django.urls import reverse

from myapp.tests.config import ErrorCodes, Views, Templates
from myapp.tests.test_Models import TestModels

# A new database is created and destroyed by each test, so no need to hide credentials
USER_NAME = "testUser1"
USER_PASSWORD = "testPassword1"

GROUP = "Administrator"

class BaseViewTest(TestCase):

    URL = Views.HOME
    TEMPLATE = Templates.HOME

    def setUp(self):
        TestModels.setUp()
        self.group = Group(name=GROUP)
        self.group.save()
        self.group.permissions.set(Permission.objects.all())

        self.user = User.objects.create_user(username=USER_NAME, password=USER_PASSWORD)
        self.user.groups.add(self.group)
        self.user.save()

        self.client = Client()
        self.client.force_login(self.user)

    def tearDown(self):
        self.group.delete()
        self.user.delete()

    def test_get_view(self, status=ErrorCodes.OK):
        resp = self.client.get(path=reverse(self.URL), follow=True)
        self.assertTemplateUsed(resp, self.TEMPLATE)
        self.assertEqual(resp.status_code, status)

        return resp
    
    def _test_get_json_response(self, status=ErrorCodes.OK, response=None):
        # private method so that it has to be called to be run instead of automatic
        resp = self.client.get(path=reverse(self.URL), follow=True)
        self.assertEqual(resp.status_code, status)
        self.assertJSONEqual(resp.content, response)

        return resp

    def _test_post_view_response(self, status=ErrorCodes.OK, payload=None, **kwargs):
        # private method so that it has to be called to be run instead of automatic
        resp = self.client.post(path=reverse(self.URL, **kwargs), data=payload, follow=True)
        self.assertEqual(resp.status_code, status)

        return resp
