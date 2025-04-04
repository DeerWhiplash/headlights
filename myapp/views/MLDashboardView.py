from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings

import logging
import requests

from myapp.models import PreprocessingStep

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
        try:
            # sends authenticated request to ML service, it just
            ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')
            response = requests.get(f"{ml_service_url}/api/models/")
            data = response.json()
            context = {
                'success': True,
                'models': data['models']
            }
            return render(request, self.template_name, context=context)
        except Exception as e:
            logger.error(f"Error getting models from ML service: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Error communicating with ML service: {str(e)}"
            }, status=500)

@method_decorator([login_required, permission_required("myapp.add_predictionmodel")], name="dispatch")  
class UploadModelView(View):
    """
    This class proxies requests for uploading ML models to the ML service.
    """
    template_name = "ml/upload_model.html"

    def get(self, request: HttpRequest) -> JsonResponse:
        preprocessing_steps = PreprocessingStep.objects.all()
        
        data = []
        for x in preprocessing_steps:
            entry = {
                "id": x.preprocessing_step_id,
                "name": x.preprocess_name
            }
            data.append(entry)
            
        context = {
            'preprocessing_steps': data
        }

        return render(request, self.template_name, context=context)
    
    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Handles the POST request for uploading a new ML model.
        Proxies the request to the ML service.
        """

        if not request.user.is_authenticated:
            return JsonResponse(
                {'status': 'error', 'message': 'Authentication required'},
                status=401
            )

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
            data.pop('preprocessingSteps', None)

            selected_steps = request.POST.getlist("preprocessingSteps")
            data["selected_steps"] = selected_steps
            
            # Send request to ML service
            response = requests.post(
                f"{ml_service_url}/api/upload-model/",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                context = {
                    'upload_success': True,
                    'message': 'Model uploaded successfully!'
                }
                return render(request, self.template_name, context=context)
            else:
                context = {
                    'error': True,
                    'message': "test"
                }
                return JsonResponse(response.json(), status=response.status_code)
            
        except Exception as e:
            logger.error(f"Error uploading model to ML service: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Error communicating with ML service: {str(e)}"
            }, status=500)
