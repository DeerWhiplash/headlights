from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import logging
import os
import pickle

from .models import Model

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def ml_dashboard(request):
    """Machine Learning dashboard view"""
    # Get all models to display on the page
    models = Model.objects.all()
    # Using the shared template path
    return render(request, 'ml/ml.html', {'models': models})

@require_http_methods(["GET"])
def models_list(request):
    """List all available ML models directly from Django database"""
    try:
        # Get all models from the database
        models = Model.objects.all()
        
        # Convert models to a list of dictionaries
        models_list = [
            {
                'id': model.model_id,
                'name': model.model_name,
                'notes': model.notes,
                'filepath': model.filepath
            }
            for model in models
        ]
        
        # If no models found, return a specific message
        if not models_list:
            return JsonResponse({
                'status': 'success',
                'message': 'no models found'
            })
        
        # Return the list of models
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

@csrf_exempt
@require_http_methods(["POST"])
def upload_model(request):
    """Upload a new ML model"""
    try:
        # Get model name and notes from the request
        model_name = request.POST.get('model_name')
        notes = request.POST.get('notes', '')
        
        # Check if model file was provided
        if 'model_file' not in request.FILES:
            return JsonResponse({
                'status': 'error',
                'message': 'No model file provided'
            }, status=400)
        
        # Get the model file
        model_file = request.FILES['model_file']
        
        # Check if file has a valid extension (e.g., .pkl)
        if not model_file.name.endswith('.pkl'):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid file format. Only .pkl files are allowed.'
            }, status=400)
        
        # Create a directory to store models if it doesn't exist
        upload_dir = os.path.join('media', 'models')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, model_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in model_file.chunks():
                destination.write(chunk)
        
        # Create a new model record in the database
        model = Model.objects.create(
            model_name=model_name,
            notes=notes,
            filepath=file_path
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Model uploaded successfully',
            'model_id': model.model_id
        })
    except Exception as e:
        logger.error(f"Error uploading model: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }, status=500)

def model_check_on_startup():
    """Check if any ML models are available on startup"""
    logger.info("Checking for available ML models on startup...")
    try:
        # Get all models from the database
        models_count = Model.objects.count()
        logger.info(f"Found {models_count} ML models in the system")
    except Exception as e:
        logger.error(f"Unexpected error checking ML models on startup: {str(e)}")

class MLUtils:
    """Utility class for ML operations"""
    
    @staticmethod
    def load_model(model_path):
        """Load a machine learning model from file"""
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None
