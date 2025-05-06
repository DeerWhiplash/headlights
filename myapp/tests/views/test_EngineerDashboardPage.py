from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from myapp.models import PredictionModel, UserProfile
from myapp.tests.config import Views, Templates, TestData, ErrorCodes

import logging
from requests.exceptions import RequestException
from unittest.mock import patch

from myapp.views.EngineerDashboardView import EngineerDashboardView

class EngineerDashboardPageTest(TestCase):

    URL = Views.MACHINE_LEARNING
    TEMPLATE = Templates.ENGINEER
    MODEL = PredictionModel

    def setUp(self):
        logging.disable(logging.ERROR)

        User = get_user_model()
        auth_id = User.objects.create_user(
            username='engineer',
            email='engineer@example.com',
            password='password'
        )
        UserProfile.objects.create(auth_id=auth_id)

        content_type = ContentType.objects.get_for_model(PredictionModel)
        engineer_permission, _ = Permission.objects.get_or_create(
            codename='add_predictionmodel',
            name='Can add prediction model',
            content_type=content_type
        )
        auth_id.user_permissions.add(engineer_permission)

        self.client.login(username='engineer', password='password')
        self.TEMPLATE = Templates.ENGINEER

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch('myapp.views.EngineerDashboardView.requests.get')
    def test_messages(self, mock_get):
        mock_response_data = {
            'status': 'success',
            'models': [
                {
                    'id': 1,
                    'name': 'simple_model',
                    'filepath': '/shared/media/models/simple.pkl',
                    'price_per_prediction': 5.0,
                    'preprocessing_steps': []
                }
            ]
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        factory = RequestFactory()
        request = factory.get(reverse(self.URL))

        User = get_user_model()
        request.user = User.objects.get(username="engineer")

        session_middleware = SessionMiddleware(lambda x: x)
        session_middleware.process_request(request)
        request.session.save()

        setattr(request, '_messages', FallbackStorage(request))

        messages.success(request, 'Model loaded successfully.')
        messages.error(request, 'Failed to upload model. Please try again.')

        response = EngineerDashboardView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    @patch('myapp.views.EngineerDashboardView.requests.get')
    def test_page_not_an_integer(self, mock_get):
        mock_response_data = {
            'status': 'success',
            'models': [
                {
                    'id': 1,
                    'name': 'simple_model',
                    'filepath': '/shared/media/models/simple.pkl',
                    'price_per_prediction': 5.0,
                    'preprocessing_steps': []
                }
            ]
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        response = self.client.get(reverse(self.URL), {'page_models': 'abc', 'page_records': 'abc'})

        self.assertEqual(response.status_code, 200)

    @patch('myapp.views.EngineerDashboardView.requests.get')
    def test_empty_page(self, mock_get):
        mock_response_data = {
            'status': 'success',
            'models': [
                {
                    'id': 1,
                    'name': 'simple_model',
                    'filepath': '/shared/media/models/simple.pkl',
                    'price_per_prediction': 5.0,
                    'preprocessing_steps': []
                }
            ]
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        response = self.client.get(reverse(self.URL), {'page_models': '999999', 'page_records': '999999'})

        self.assertEqual(response.status_code, 200)

    @patch('myapp.views.EngineerDashboardView.requests.get')
    def test_bad_response_from_ml_get(self, mock_get):
        mock_get.side_effect = RequestException("ML service down")

        response = self.client.get(reverse(self.URL))

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
        response.content.decode(),
        {
            'status': 'error',
            'message': 'Error communicating with ML service: ML service down'
        }
    )

    def test_unauthenticated_model_upload(self):
        self.URL = Views.API_UPLOAD_MODEL
        self.client.logout()
        
        # Test uploading a model without being logged in
        valid_file = SimpleUploadedFile("test.pkl", b"file_content", content_type="application/octet-stream")
        payload = {'model_name': TestData.NAME, 'notes': "", 'model_file': valid_file}
        response = self.client.post(path=reverse(self.URL), data=payload)

        self.assertEqual(response.status_code, ErrorCodes.REDIRECT)

    @patch('myapp.views.EngineerDashboardView.requests.post')
    def test_post_view_success(self, mock_post):
        mock_post.return_value.status_code = 200

        file_data = SimpleUploadedFile(
            "test_model.pkl",
            b"File binary data",
            content_type="application/octet-stream"
        )

        response = self.client.post(
            reverse(self.URL),
            data={'model_file': file_data},
            format='multipart'
        )

        self.assertEqual(response.status_code, 302)
        mock_post.assert_called_once()
        self.assertIn("/api/upload-model/", mock_post.call_args[0][0])

    @patch('myapp.views.EngineerDashboardView.requests.post')
    def test_bad_response_from_ml_post(self, mock_post):
        mock_post.side_effect = RequestException("ML service down")

        file_data = SimpleUploadedFile(
            "test_model.pkl",
            b"File binary data",
            content_type="application/octet-stream"
        )

        response = self.client.post(
            reverse(self.URL),
            data={'model_file': file_data},
            format='multipart'
        )

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
        response.content.decode(),
        {
            'status': 'error',
            'message': 'Error communicating with ML service: ML service down'
        }
    )

    def test_post_view_failure_no_model_file(self):
        response = self.client.post(reverse(self.URL))
        self.assertEqual(response.status_code, 400)
