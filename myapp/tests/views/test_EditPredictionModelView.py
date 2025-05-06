from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from myapp.models import PredictionModel, UserProfile
from myapp.tests.config import Views, Templates

from unittest.mock import patch

from myapp.views.EngineerDashboardView import EditPredictionModelView

class EditPredictionModelViewTests(TestCase):

    URL = Views.EDIT_MODEL
    TEMPLATE = Templates.ENGINEER_EDIT_MODEL
    MODEL = PredictionModel
    
    def setUp(self):
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
    
    @patch('myapp.views.EngineerDashboardView.requests.get')
    def test_get_view(self, mock_get):
        mock_response_data = {
            'status': 'success',
            'models': [
                {
                    'id': 1,
                    'name': 'simple_model',
                    'filepath': '/shared/media/models/simple.pkl',
                    'price_per_prediction': 5.0,
                    'notes': '',
                    'preprocessing_steps': []
                }
            ]
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        factory = RequestFactory()
        request = factory.get(reverse("edit_model", args=[1]))

        User = get_user_model()
        request.user = User.objects.get(username="engineer")

        session_middleware = SessionMiddleware(lambda x: x)
        session_middleware.process_request(request)
        request.session.save()

        response = EditPredictionModelView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        
    @patch('myapp.views.EngineerDashboardView.requests.post')
    def test_post_view_success(self, mock_post):
        mock_post.return_value.status_code = 200
        
        form_values = {
            "model_name": "model",
            "notes": "",
            "price_per_prediction": 1,
            "data_processing_options": []
        }

        response = self.client.post(
            reverse(self.URL, args=[1]),
            data=form_values,
        )

        self.assertEqual(response.status_code, 302)
        mock_post.assert_called_once()
        self.assertIn("api/model/edit/1/", mock_post.call_args[0][0])
        
    @patch('myapp.views.EngineerDashboardView.requests.post')
    def test_post_view_failure(self, mock_post):
        mock_post.return_value.status_code = 500

        form_values = {
            "model_name": "model",
            "notes": "",
            "price_per_prediction": 1,
            "data_processing_options": []
        }

        response = self.client.post(
            reverse(self.URL, args=[1]),
            data=form_values,
        )

        self.assertEqual(response.status_code, 302)
