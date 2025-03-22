from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import logging
import requests

# Configure logging
logger = logging.getLogger(__name__)

@method_decorator([login_required, permission_required("myapp.add_predictionmodel")], name="dispatch")
class MLDashboardView(View):
    """
    This class handles rendering the machine learning dashboard page.
    """

    template_name = "ml/ml.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the GET request for the machine learning dashboard page.
        Renders the ML dashboard template.
        """
        logger.info(f"{request.user} accessed the machine learning dashboard page.")
        return render(request, self.template_name)

@method_decorator(require_http_methods(["GET"]), name="dispatch")
class ModelListView(View):
    """
    This class proxies requests for listing ML models to the ML service.
    """
    
    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Handles the GET request for listing all available ML models.
        Proxies the request to the ML service.
        """
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
            
        try:
            # sends authenticated request to ML service, it just
            ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')
            response = requests.get(f"{ml_service_url}/api/models/")
            return JsonResponse(response.json())
        except Exception as e:
            logger.error(f"Error getting models from ML service: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Error communicating with ML service: {str(e)}"
            }, status=500)

@method_decorator(csrf_exempt, name="dispatch")
class UploadModelView(View):
    """
    This class proxies requests for uploading ML models to the ML service.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Handles the POST request for uploading a new ML model.
        Proxies the request to the ML service.
        """
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
            
        try:
            ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')
            # Forward files and data to the ML service
            model_file = request.FILES.get('model_file')
            
            if not model_file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No model file provided'
                }, status=400)
            
            # Create multipart form data request
            files = {'model_file': (model_file.name, model_file, model_file.content_type)}
            data = {k: v for k, v in request.POST.items()}
            
            # Send request to ML service
            response = requests.post(
                f"{ml_service_url}/api/upload-model/",
                files=files,
                data=data
            )
            
            # Return the ML service response
            return JsonResponse(response.json(), status=response.status_code)
            
        except Exception as e:
            logger.error(f"Error uploading model to ML service: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Error communicating with ML service: {str(e)}"
            }, status=500)
