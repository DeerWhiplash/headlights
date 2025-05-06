from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.forms.models import model_to_dict
from django.test import RequestFactory, TestCase
from django.urls import reverse

import logging
import requests
from unittest.mock import patch

from myapp.tests.test_BaseView import BaseViewTest, USER_NAME, USER_PASSWORD
from myapp.tests.config import Views, Templates, TestData, ErrorCodes

from myapp.views.CustomerDashBoardView import create_uploaded_record, get_claim_prediction, PredictionFeedbackView
from myapp.models import Claim, Feedback, UploadedRecord, PredictionModel

class CustomerDashboardTest(BaseViewTest, TestCase):

    URL = Views.CUSTOMER_DASHBOARD
    TEMPLATE = Templates.CUSTOMER

    def setUp(self):
        logging.disable(logging.ERROR)
        BaseViewTest.setUp(self)

        self.claim = Claim.objects.first()
        self.model = PredictionModel.objects.first()

    def tearDown(self):
        logging.disable(logging.NOTSET)
        BaseViewTest.tearDown(self)
    
    @patch('myapp.models.UploadedRecord.objects.create')
    def test_create_uploaded_record_exception(self, mock_create):
        """ Test that function handles unexpected exception """
        record = {
            'user': self.user_profile,
            'claim': self.claim,
            'model_id': self.model,
            'prediction': 100 # arbitrary value
        }

        # mock db create to raise an error
        mock_create.side_effect = IntegrityError("Simulated database error")
        
        # function catches unexpected errors as a runtime error
        with self.assertRaises(RuntimeError) as context:
            create_uploaded_record(record)

        self.assertEqual(str(context.exception), "An unexpected error occurred while saving the record")
    
    def test_create_uploaded_record_success(self):
        """ Test that function successfully creates record"""
        record = {
            'user': self.user_profile,
            'claim': self.claim,
            'model_id': self.model,
            'prediction': 100 # arbitrary value
        }

        uploaded_record = create_uploaded_record(record)

        self.assertTrue(isinstance(uploaded_record, UploadedRecord))
        # Delete the uploaded record from the database
        UploadedRecord.objects.filter(user_id=self.user_profile).delete()


    def test_create_uploaded_record_value_error(self):
        """ Test that function throws value error if missing key """
        record = {
            'user': self.user_profile,
            'claim': self.claim,
        }

        with self.assertRaises(ValueError) as context:
            create_uploaded_record(record)

        error_message = context.exception.args[0]
        keys_in_message = set(key.strip("'") for key in error_message.replace("Missing required keys in record: ", "").strip("{}").split(", "))
        expected_keys = set(['model_id', 'prediction'])

        self.assertSetEqual(keys_in_message, expected_keys)


    def test_get_view(self):
        self.TEMPLATE = Templates.LOGIN
        self.client.logout()

        BaseViewTest.test_get_view(self)

        self.client.login(username=USER_NAME, password=USER_PASSWORD)
        self.TEMPLATE = Templates.CUSTOMER

        BaseViewTest.test_get_view(self)

    @patch("requests.post")
    def test_get_prediction_connection_error(self, mock_post):
        """Test that a connection error is handled properly."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection failed")

        with self.assertRaises(ConnectionError) as context:
            get_claim_prediction(self.claim, self.model)

        self.assertEqual(str(context.exception), "Error connecting to ML service")

    @patch("requests.post")
    def test_get_prediction_json_decode_error(self, mock_post):
        """Test that a JSONDecodeError is handled correctly."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = requests.exceptions.JSONDecodeError("Expecting value", "", 0)

        with self.assertRaises(ValueError) as context:
            get_claim_prediction(self.claim, self.model)

        self.assertEqual(str(context.exception), "Invalid JSON response from ML service")

    @patch("requests.post")
    def test_get_prediction_unexpected_response_format(self, mock_post):
        """Test that a response without 'data' raises a ValueError."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {}

        with self.assertRaises(ValueError) as context:
            get_claim_prediction(self.claim, self.model)

        self.assertEqual(str(context.exception), "ML service response format is invalid")
    
    @patch("requests.post")
    def test_get_prediction_missing_prediction_key(self, mock_post):
        """Test that a response missing 'prediction' in 'data' raises a ValueError."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": {}}

        with self.assertRaises(ValueError) as context:
            get_claim_prediction(self.claim, self.model)

        self.assertEqual(str(context.exception), "Prediction key missing from ML response")

    @patch("requests.post")
    def test_get_prediction_success(self, mock_post):
        """ Test that the function correctly processes a successful response. """

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {"prediction": 0.85}
        }

        prediction = get_claim_prediction(self.claim, self.model)
        
        claimDict = model_to_dict(self.claim)
        claimDict.pop('claim_id')

        self.assertEqual(prediction, 0.85)

        mock_post.assert_called_once_with(
            f"{getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')}/api/model/predict/",
            json={'model_id': self.model.model_id, 'data': claimDict},
            timeout=10
        )

    def test_get_uploaded_record_does_not_exist(self):
        session = self.client.session
        session['uploaded_record_id'] = 9999 # Assuming 9999 is an invalid ID
        session.save()

        BaseViewTest.test_get_view(self)

        # Check if the session key is removed
        self.assertNotIn('uploaded_record_id', self.client.session)
         
    @patch("myapp.views.CustomerDashBoardView.get_claim_prediction")
    def test_post_view_valid(self, mock_get_claim_prediction):
        """ Test view creates record on valid request """
        mock_get_claim_prediction.return_value = 1000
        
        form_data = {'uploaded_claims': self.claim.claim_id, 'model': self.model.model_id}
        
        BaseViewTest._test_post_view_response(self, payload=form_data)

        # Delete the uploaded record from the database
        UploadedRecord.objects.filter(user_id=self.user_profile).delete()

    def test_post_view_invalid(self):
        form_data = {'uploaded_claims': 0}

        BaseViewTest._test_post_view_response(self, status=ErrorCodes.BAD_REQUEST, payload=form_data)

    def test_post_user_settlement_valid(self):
        record = {
            'user': self.user_profile,
            'claim': self.claim,
            'model_id': self.model,
            'prediction': 100 # arbitrary value
        }

        uploaded_record = create_uploaded_record(record)

        session = self.client.session
        session['uploaded_record_id'] = uploaded_record.uploaded_record_id
        session.save()

        response = self.client.post(
            reverse(self.URL),
            data={'user_settlement': 150}
        )

        uploaded_record.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(uploaded_record.user_settlement, 150)

        UploadedRecord.objects.filter(uploaded_record_id=uploaded_record.uploaded_record_id).delete()

    def test_post_user_settlement_invalid_form(self):
        record = {
            'user': self.user_profile,
            'claim': self.claim,
            'model_id': self.model,
            'prediction': 100 # arbitrary value
        }

        uploaded_record = create_uploaded_record(record)

        session = self.client.session
        session['uploaded_record_id'] = uploaded_record.uploaded_record_id
        session.save()

        response = self.client.post(
            reverse(self.URL),
            data={'user_settlement': ''}
        )

        uploaded_record.refresh_from_db()

        self.assertEqual(response.status_code, 400)
        self.assertIsNone(uploaded_record.user_settlement)

        UploadedRecord.objects.filter(uploaded_record_id=uploaded_record.uploaded_record_id).delete()

    def test_post_user_settlement_missing_record_id(self):
        response = self.client.post(
            reverse(self.URL),
            data={'user_settlement': 150}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No uploaded record found in session", response.content)

    def test_post_user_settlement_invalid_record_id(self):
        session = self.client.session
        session['uploaded_record_id'] = 9999  # Non-existent ID
        session.save()

        response = self.client.post(
            reverse(self.URL),
            data={'user_settlement': '150'}
        )

        self.assertEqual(response.status_code, 404)

class CustomerUploadTest(BaseViewTest, TestCase):
    
    URL = Views.CUSTOMER_UPLOAD
    TEMPLATE = Templates.CUSTOMER
    
    def setUp(self):
        return BaseViewTest.setUp(self)
    
    def test_get_view(self):
        BaseViewTest.test_get_view(self)

    def test_claim_upload(self):

        # Test uploading a model with incorrect file type
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        payload = {'claims_file': invalid_file}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        self.assertJSONEqual(
            response.content,
            {
                'status': "error",
                'message': "Invalid file type"
            }
        )
        
        # Test uploading a model with correct file type but incorrect columns
        with open('myapp/tests/data/InvalidTestClaimData.csv', "rb") as f:
            data = f.read()
            
        valid_file = SimpleUploadedFile("test.csv", data)
        payload = {'claims_file': valid_file}
        response = BaseViewTest._test_post_view_response(self, payload=payload)

        self.assertJSONEqual(
            response.content,
            {
                'status': "confirmationRequired",
                'message': "The following columns could not be found in the uploaded file: Gender\n\nThe following columns are either missnamed or invalid: ExcessCol"
            }
        )

        # Test uploading a model with correct file type and valid columns
        with open('myapp/tests/data/TestClaimData.csv', "rb") as f:
            data = f.read()
            
        valid_file = SimpleUploadedFile("test.csv", data)
        payload = {'claims_file': valid_file, 'trainingData': True}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
            
        self.assertJSONEqual(
            response.content,
            {
                'status': "success",
                'message': "",
            }
        )

class PredictionFeedbackTest(BaseViewTest, TestCase):
    
    URL = Views.PREDICTION_FEEDBACK
    TEMPLATE = Templates.PREDICTION_FEEDBACK
    
    def setUp(self):
        return BaseViewTest.setUp(self)
    
    def test_get_view(self):
        BaseViewTest.test_get_view(self)

    def test_valid_feedback_form(self):
        form = PredictionFeedbackView.form_class
        # Check if the form is the correct form
        self.assertEqual(form.Meta.model.__name__, "Feedback")

        # Check if the form is valid
        form_data = {'rating' : TestData.RATING, 'notes' : TestData.NAME}
        form = form(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_feedback_form(self):
        form = PredictionFeedbackView.form_class
        # Check if the form is the correct form
        self.assertEqual(form.Meta.model.__name__, "Feedback")

        # Check if the form is invalid with out of range rating
        form_data = {'rating' : 0, 'notes' : ""}
        form = form(data=form_data)
        self.assertFalse(form.is_valid())

    def test_post_view(self):
        factory = RequestFactory()
        form_data = {'rating' : TestData.RATING, 'notes' : TestData.NAME}

        request = factory.post(self.URL, form_data)
        request.user = self.user

        # Initialise SessionMiddleware
        middleware = SessionMiddleware(lambda x : None)
        middleware.process_request(request)
        request.session['uploaded_record_id'] = 1
        request.session.save()

        # Initialise MessageMiddleware
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = PredictionFeedbackView.as_view()(request)
        self.assertTrue(response)

        # Check if the feedback was saved to the database
        feedback = Feedback.objects.filter(user_id=self.user_profile)
        for f in feedback:
            self.assertEqual(f.rating, TestData.RATING)
            self.assertEqual(f.notes, TestData.NAME)

            # Check if the feedback was assigned to the uploaded record, and delete it
            uploaded_record = UploadedRecord.objects.get(feedback_id=f)
            self.assertEqual(uploaded_record.feedback_id, f)
            uploaded_record.delete()

            # Delete the feedback from the database
            f.delete()

class CustomerPreprocessingTest(BaseViewTest, TestCase):
    URL = Views.CUSTOMER_PREPROCESSING
    TEMPLATE = Templates.CUSTOMER_PREPROCESSING
    
    def test_get_view(self):
        BaseViewTest.test_get_view(self)
        
    def test_preprocess_upload(self):
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        payload = {'claims_file': invalid_file}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        context = response.context.pop()
        self.assertEqual(context["status"], "error")
        
        with open('myapp/tests/data/InvalidTestClaimData.csv', "rb") as f:
            data = f.read()
        valid_file = SimpleUploadedFile("test.csv", data)
        payload = {'claims_file': valid_file}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        context = response.context.pop()
        self.assertEqual(context["status"], "confirmationRequired")
        
        with open('myapp/tests/data/TestClaimData.csv', "rb") as f:
            data = f.read()
        valid_file = SimpleUploadedFile("test.csv", data)
        payload = {'claims_file': valid_file}
        response = BaseViewTest._test_post_view_response(self, payload=payload)
        self.assertEqual(response.get('Content-Disposition'), "attachment; filename=ProcessedClaims.csv")
