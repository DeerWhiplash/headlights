from django.test import TestCase

from myapp.tests.config import ErrorCodes, Views, Templates
from myapp.tests.test_BaseView import BaseViewTest

class TestErrorViews(TestCase):

    def test_index_page(self):
        self.TEMPLATE = Templates.HOME
        self.URL = Views.HOME
        return BaseViewTest.test_get_view(self, status=ErrorCodes.OK)

    def test_bad_request(self):
        self.TEMPLATE = Templates.ERROR_400
        self.URL = Views.ERROR_400
        return BaseViewTest.test_get_view(self, status=ErrorCodes.BAD_REQUEST)

    def test_forbidden(self):
        self.TEMPLATE = Templates.ERROR_403
        self.URL = Views.ERROR_403
        return BaseViewTest.test_get_view(self, status=ErrorCodes.FORBIDDEN)

    def test_not_found(self):
        self.TEMPLATE = Templates.ERROR_404
        self.URL = Views.ERROR_404
        return BaseViewTest.test_get_view(self, status=ErrorCodes.NOT_FOUND)

    def test_server_error(self):
        self.TEMPLATE = Templates.ERROR_500
        self.URL = Views.ERROR_500
        return BaseViewTest.test_get_view(self, status=ErrorCodes.SERVER_ERROR)
