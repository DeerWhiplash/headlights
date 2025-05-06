# Temporary test until front-end functionality added to MLDashboard to predict
# TODO: move test to myapp/tests/views/test_MLDashboardPage.py when predict FE implemented.
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
import logging
import os
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, mock_open, MagicMock

from ml_app.models import PredictionModel, PreprocessingStep, PreprocessingModelMap

class ModelListTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/models/'

        filepath = '/shared/media/models/limited_model.pkl'
        if os.getenv('GITHUB_ACTIONS') == 'true':
            filepath = '../dataset/limited_model.pkl'

        self.model = PredictionModel.objects.create(
            model_id=1,
            model_name='test_model',
            model_type='default',
            notes='',
            filepath=filepath
        )
        
        step = PreprocessingStep.objects.create(
            preprocessing_step_id = 1,
            preprocess_name = 'create_days_between_col'
        )

        PreprocessingModelMap.objects.create(
            preprocessing_model_map_id = 1,
            preprocessing_step_id=step,
            model_id=self.model
        )

        logging.disable(logging.ERROR)
    
    def tearDown(self):
        logging.disable(logging.NOTSET)
        return super().tearDown()

    def test_get_model_success(self):
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('test_model', data['models'][0]['name'])
        self.assertEqual(['create_days_between_col'], data['models'][0]['preprocessing_steps'])
        
        response = self.client.get(self.url + "1/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('test_model', data['models'][0]['name'])
        self.assertEqual(['create_days_between_col'], data['models'][0]['preprocessing_steps'])

    def test_no_models_found(self):

        PreprocessingModelMap.objects.all().delete()
        PredictionModel.objects.all().delete()

        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('no models found', data['message'])


class ModelPredictTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/model/predict/'

        filepath = '/shared/media/models/limited_model.pkl'
        if os.getenv('GITHUB_ACTIONS') == 'true':
            filepath = '../dataset/limited_model.pkl'

        self.model = PredictionModel.objects.create(
            model_id=1,
            model_name='test_model',
            model_type='default',
            notes='',
            filepath=filepath)

        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        return super().tearDown()
    
    def test_missing_model_id(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'PredictionModel ID not supplied')
    
    def test_non_existent_model(self):
        response = self.client.post(self.url, {'model_id': 99999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'PredictionModel supplied does not exist')
    
    def test_empty_data(self):
        response = self.client.post(self.url, {'model_id': 1, 'data': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'PredictionModel name not supplied')
    
    def test_internal_server_error_on_model_build(self):
        PredictionModel.objects.create(model_id=2)

        response = self.client.post(self.url, {'model_id': 2, 'data': {'feature1': 1}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Failed to load model: 2')
    
    def test_successful_prediction(self):
        with patch('ml_app.MLModelService.ClaimsModel.predict', return_value={'result': 0.95}):
            response = self.client.post(self.url, {'model_id': 1, 'data': {'feature1': 1}}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('data', response.data)
            self.assertEqual(response.data['data']['prediction'], {'result': 0.95})

class ModelUploadTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/upload-model/'

        self.test_file = SimpleUploadedFile(
            "test_model.pkl", b"fake-model-content", content_type="application/octet-stream"
        )
        
        self.preprocessingStep = PreprocessingStep.objects.create(
            preprocessing_step_id = 1,
            preprocess_name = 'create_days_between_col'
        )

        logging.disable(logging.ERROR)

    def test_invalid_preprocessing_ids(self):
        data = {
            'model_name': 'TestModel',
            'notes': 'test notes',
            'data_processing_options': [10000, 20000]
        }

        response = self.client.post(self.url, data={
            **data,
            'model_file': self.test_file
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Invalid preprocessing steps provided')
        self.assertFalse(PredictionModel.objects.filter(model_name='TestModel').exists())

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_model_upload_success(self, mock_makedirs, mock_file_open):
        self.test_file.chunks = MagicMock(return_value=[b"fake-model-content"])

        data = {
            'model_name': 'TestModel',
            'notes': 'test notes',
            'data_processing_options': [self.preprocessingStep.preprocessing_step_id]
        }

        response = self.client.post(self.url, data={
            **data,
            'model_file': self.test_file
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(PredictionModel.objects.filter(model_name='TestModel').exists())
        mock_makedirs.assert_called_once_with('/shared/media/models', exist_ok=True)
        mock_file_open.assert_called_once()  
        
        # Tidy up
        model = PredictionModel.objects.filter(model_name='TestModel').get()
        PreprocessingModelMap.objects.filter(model_id=model).delete()
        model.delete()

    def test_missing_model_file(self):
         
        data = {
            'model_name': 'TestModel',
            'notes': 'test notes',
            'data_processing_options': [self.preprocessingStep.preprocessing_step_id]
        }

        response = self.client.post(self.url, data={
            **data,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'No model file provided')
        self.assertFalse(PredictionModel.objects.filter(model_name='TestModel').exists())

class EditModelTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.model_id = 2
        self.url = f'/api/model/edit/{self.model_id}/'
        
        filepath = '/shared/media/models/limited_model.pkl'
        
        self.model = PredictionModel.objects.create(
            model_id=self.model_id,
            model_name='test_model',
            model_type='default',
            notes='',
            filepath=filepath
        )
        
        self.preprocessingStep = PreprocessingStep.objects.create(
            preprocessing_step_id = 1,
            preprocess_name = 'create_days_between_col'
        )
        
    def test_edit_model_success(self):
        data = {
            "model_name": "EditModel",
            "notes": "",
            "price_per_prediction": 1,
            "data_processing_options": [1]
        }
        logging.warning(self.model_id)
        logging.warning(self.url)
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(PredictionModel.objects.filter(model_name='EditModel').exists())
        
