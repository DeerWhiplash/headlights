from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import logging
import os

from .MLModelService import ClaimsModel, ModelLoadError
from .models import PredictionModel, PreprocessingStep, PreprocessingModelMap

# Configure logging
logger = logging.getLogger(__name__)

def model_check_on_startup() -> None:
    """
    This method checks if any ML models are available on startup.
    """
    logger.info("Checking for available ML models on startup...")
    try:
        # Get all models from the database
        models_count = PredictionModel.objects.count()
        logger.info(f"Found {models_count} ML models in the system")
    except Exception as e:
        logger.error(f"Unexpected error checking ML models on startup: {str(e)}")

@method_decorator(login_required, name="dispatch")
class MLDashboardView(View):
    """
    This class handles the rendering and processing of the machine learning dashboard page.
    """
    template_name = "engineer.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the GET request for the machine learning dashboard page.
        """
        # Get all models to display on the page
        models = PredictionModel.objects.all()
        logger.info(f"{request.user} accessed the machine learning dashboard page.")
        return render(request, self.template_name, {'models': models})

class ModelListView(View):
    """
    This class handles the listing of all available ML models directly from the Django database.
    """
    def get(self, request: HttpRequest, model_id=None) -> JsonResponse:
        """
        Handles the GET request for listing all available ML models.
        """
        try:
            preprocessing_steps_queryset = PreprocessingModelMap.objects.select_related('preprocessing_step_id')

            if model_id:
                models = PredictionModel.objects.prefetch_related(
                    Prefetch('preprocessingmodelmap_set', queryset=preprocessing_steps_queryset, to_attr='preprocessing_steps')
                ).filter(model_id=model_id)
            else:
                models = PredictionModel.objects.prefetch_related(
                    Prefetch('preprocessingmodelmap_set', queryset=preprocessing_steps_queryset, to_attr='preprocessing_steps')
                ).all()

            models_list = [
                {
                    'id': model.model_id,
                    'name': model.model_name,
                    'notes': model.notes,
                    'filepath': model.filepath,
                    'price_per_prediction': model.price_per_prediction,
                    'preprocessing_steps': [map_item.preprocessing_step_id.preprocess_name for map_item in model.preprocessing_steps]
                }
                for model in models
            ]
            
            # If no models found, return a specific message
            if not models_list:
                return JsonResponse({
                    'status': 'success',
                    'message': 'no models found',
                    'models': []
                })
            
            logger.info(f"Successfully retrieved {len(models_list)} models from the database.")
            return JsonResponse({
                'status': 'success',
                'models': models_list
            })

        except Exception as e:
            logger.error(f"Error getting models: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"An unexpected error occurred: {str(e)}"
            }, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class UploadModelView(View):
    """
    This class handles the uploading of a new ML model.
    """
    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Handles the POST request for uploading a new ML model.
        """            
        try:
            # Get model name and notes from the request
            model_name = request.POST.get('model_name')
            notes = request.POST.get('notes', '')
            data_processing_options = request.POST.get('data_processing_options')
            price_per_prediction = request.POST.get('price_per_prediction')
            
            # Check if model file was provided
            if 'model_file' not in request.FILES:
                logger.info("No model provided in the request.")
                return JsonResponse({
                    'status': 'error',
                    'message': 'No model file provided'
                }, status=400)
            
            # Get the model file
            model_file = request.FILES['model_file']
            
            # Check if file has a valid extension (e.g., .pkl)
            if not model_file.name.endswith('.pkl'):
                logger.info("Invalid file format. Only .pkl files are allowed.")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid file format. Only .pkl files are allowed.'
                }, status=400)
            
            if(data_processing_options):
                preprocessing_steps = PreprocessingStep.objects.filter(preprocessing_step_id__in=data_processing_options)
                if(not preprocessing_steps):
                    logger.info("Preprocessing ids do not exist")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid preprocessing steps provided'
                    }, status=400)

            # Create a directory to store models if it doesn't exist
            upload_dir = os.path.join('/shared/media', 'models')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, model_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in model_file.chunks():
                    destination.write(chunk)
            
            # Create a new model record in the database
            model = PredictionModel.objects.create(
                model_name=model_name,
                notes=notes,
                filepath=file_path,
                price_per_prediction=price_per_prediction,
            )

            objects = []
            if(data_processing_options):
                for x in data_processing_options:
                    objects.append(PreprocessingModelMap(preprocessing_step_id_id = int(x), model_id_id = model.model_id))

                PreprocessingModelMap.objects.bulk_create(objects)
                
            logger.info(f"PredictionModel '{model_name}' uploaded successfully with ID {model.model_id}.")
            return JsonResponse({
                'status': 'success',
                'message': 'PredictionModel uploaded successfully',
                'model_id': model.model_id
            })
        
        except Exception as e:
            logger.error(f"Error uploading model: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"An unexpected error occurred: {str(e)}"
            }, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class EditModelView(View):
    def post(self, request: HttpRequest, model_id) -> JsonResponse:
        model_name = request.POST.get('model_name')
        notes = request.POST.get('notes', '')
        data_processing_options = request.POST.get('data_processing_options')
        price_per_prediction = request.POST.get('price_per_prediction')
        
        model = PredictionModel.objects.get(model_id=model_id)
        model.model_name = model_name or model.model_name
        model.notes = notes
        model.price_per_prediction = price_per_prediction or model.price_per_prediction
        model.save()
        
        PreprocessingModelMap.objects.filter(model_id=model_id).delete()
        objects = []
        if data_processing_options:
            for x in data_processing_options:
                objects.append(PreprocessingModelMap(preprocessing_step_id_id = int(x), model_id_id = model.model_id))
                
            PreprocessingModelMap.objects.bulk_create(objects)

        return JsonResponse({
            'status': 'success',
            'message': 'PredictionModel edited successfully',
        }, status=status.HTTP_200_OK)

            
class ModelPredict(APIView):
    
    def post(self, request, format=None):
        model_id = request.data.get('model_id')
        
        if(not model_id):
            return Response({'message': 'PredictionModel ID not supplied'}, status=status.HTTP_400_BAD_REQUEST)
        
        if (not PredictionModel.objects.filter(model_id=model_id)):
            return Response({'message': 'PredictionModel supplied does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        model = PredictionModel.objects.filter(model_id=model_id).first()

        try:
            model = ClaimsModel(model=model)
        except ModelLoadError as e:
            logger.error(f"Error building model: {e}")
            return Response({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)

        data_df = pd.DataFrame([request.data.get('data')])

        if(data_df.empty):
            return Response({'message': 'PredictionModel name not supplied'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            prediction = model.predict(data_df)
        except Exception as e:
            return Response({'message': str(e)}, status.HTTP_400_BAD_REQUEST)

        response_data = {'prediction' : prediction}
        return Response({'data' : response_data}, status=status.HTTP_200_OK)

class HealthCheckView(View):
    """
    Simple health check endpoint to verify the service is running.
    """
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'status': 'healthy'})
