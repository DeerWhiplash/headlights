from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import os
import logging
from .models import Claim

# Configure logging
logger = logging.getLogger(__name__)

# ML service URL
ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://ml-service:8001")

def index(request):
    """View function for site home page - shows claim count"""
    # Add extensive logging to debug the redirect issue
    logger.info(f"Rendering index page for user: {request.user}")
    
    # Get the count of claims
    num_claims = Claim.objects.all().count()
    logger.info(f"Found {num_claims} claims")
    
    # Explicitly render the index.html template
    context = {
        'num_claims': num_claims
    }
    return render(request, 'index.html', context=context)

@login_required
def ml_dashboard(request):
    """Render the ML dashboard template directly instead of redirecting to ML service"""
    try:
        # Get models from the ML service API
        response = requests.get(f"{ML_SERVICE_URL}/api/models/")
        models = response.json().get('models', [])
    except Exception as e:
        logger.error(f"Error fetching models from ML service: {str(e)}")
        models = []
    
    # Render the ML dashboard template directly
    return render(request, 'ml/ml.html', {'models': models})

@require_http_methods(["GET"])
def models_list(request):
    """Proxy the models list request to the ML service"""
    try:
        response = requests.get(f"{ML_SERVICE_URL}/api/models/")
        return JsonResponse(response.json())
    except Exception as e:
        logger.error(f"Error connecting to ML service: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f"Error connecting to ML service: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_model(request):
    """Proxy the upload model request to the ML service"""
    try:
        # Forward the entire request
        files = {'model_file': request.FILES.get('model_file')}
        data = {
            'model_name': request.POST.get('model_name'),
            'notes': request.POST.get('notes', '')
        }
        response = requests.post(f"{ML_SERVICE_URL}/api/upload-model/", files=files, data=data)
        return JsonResponse(response.json())
    except Exception as e:
        logger.error(f"Error connecting to ML service: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f"Error connecting to ML service: {str(e)}"
        }, status=500)
