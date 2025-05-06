from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

import traceback
import logging
import requests

from myapp.models import PreprocessingStep, UploadedRecord

# Configure logging
logger = logging.getLogger(__name__)

class UploadModelForm(forms.Form):
    model_name = forms.CharField(
        label="Model Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'modelName',
            'class': 'form-control'
        })
    )
    
    notes = forms.CharField(
        label="Notes",
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'id': 'modelNotes',
            'rows': 3,
            'class': 'form-control',
        })
    )

    data_processing_options = forms.MultipleChoiceField(
        label="Select Preprocessing Steps",
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'id': 'preprocessing_steps',
        })
    )

    model_file = forms.FileField(
        label="Model File (.pkl)",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'id': 'modelFile',
            'accept': '.pkl',
            'class': 'form-control',
        })
    )

    price_per_prediction = forms.FloatField(
        label="Price Per Prediction",
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'pricePerPrediction',
            'class': 'form-control',
        })
    )

    def __init__(self, edit_existing=False, *args, **kwargs):
        preprocessing_steps = kwargs.pop('preprocessing_steps', [])
        super().__init__(*args, **kwargs)
        self.fields['data_processing_options'].choices = [
            (step.preprocessing_step_id, step.preprocess_name) for step in preprocessing_steps
        ]
        
        if edit_existing:
            self.fields["model_file"] = None

@method_decorator([login_required, permission_required("myapp.add_predictionmodel")], name="dispatch")
class EngineerDashboardView(View):
    """
    This class handles rendering the machine learning dashboard page.
    """

    template_name = "engineer.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the GET request for the machine learning dashboard page.
        Renders the ML dashboard template.
        """
        logger.info(f"{request.user} accessed the machine learning dashboard page.")
        try:
            error = False
            message = None

            stored_messages = messages.get_messages(request)
            for msg in stored_messages:
                if msg.tags == 'success':
                    message = str(msg)
                elif msg.tags == 'error':
                    error = True
                    message = str(msg)

            # sends authenticated request to ML service, it just
            ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')
            response = requests.get(f"{ml_service_url}/api/models/")
            response_data = response.json()

            # Build preprocessing data
            for x in response_data['models']:
                if isinstance(x['preprocessing_steps'], list):
                    x['preprocessing_steps'] = ", ".join(x['preprocessing_steps'])

            models_list = response_data.get('models', [])
            paginator = Paginator(models_list, 10)
            page_models = request.GET.get('page_models')

            # Pagination for models table
            try:
                models = paginator.page(page_models)
            except PageNotAnInteger:
                models = paginator.page(1)
            except EmptyPage:
                models = paginator.page(paginator.num_pages)

            uploaded_records_list = UploadedRecord.objects.all().order_by('-uploaded_record_id')
            records_paginator = Paginator(uploaded_records_list, 10)
            page_records = request.GET.get('page_records')

            try:
                uploaded_records = records_paginator.page(page_records)
            except PageNotAnInteger:
                uploaded_records = records_paginator.page(1)
            except EmptyPage:
                uploaded_records = records_paginator.page(records_paginator.num_pages)

            num_predictions = UploadedRecord.objects.all().count()
            preprocessing_steps = PreprocessingStep.objects.all()
            form = UploadModelForm(preprocessing_steps=preprocessing_steps)

            context = {
                'form': form,
                'error': error,
                'message': message,
                'models': models,
                'uploaded_records': uploaded_records,
                'num_predictions': num_predictions,
            }

            return render(request, self.template_name, context=context)

        except Exception as e:
            logger.error(f"Error getting models from ML service: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"Error communicating with ML service: {str(e)}"
            }, status=500)
    
    def post(self, request: HttpRequest) -> JsonResponse:
        """
        Handles the POST request for uploading a new ML model.
        Proxies the request to the ML service.
        """

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
            data = dict(request.POST.items())
            
            # Send request to ML service
            response = requests.post(
                f"{ml_service_url}/api/upload-model/",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                messages.success(request, 'Model uploaded successfully!')
            else:
                messages.error(request, 'Failed to upload model. Please try again.')

            return redirect("engineer")

        except Exception as e:
            logger.error(f"Error uploading model to ML service: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f"Error communicating with ML service: {str(e)}"
            }, status=500)    

@method_decorator([login_required, permission_required("myapp.add_predictionmodel")], name="dispatch")
class EditPredictionModelView(View):
    template_name = "edit_model.html"

    def get(self, request: HttpRequest, model_id=0) -> HttpResponse: 
            # sends authenticated request to ML service
            ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')
            response = requests.get(f"{ml_service_url}/api/models/{model_id}/")
            response_data = response.json()

            # Build preprocessing data
            for x in response_data['models']:
                if isinstance(x['preprocessing_steps'], list):
                    x['preprocessing_steps'] = ", ".join(x['preprocessing_steps'])

            model = response_data.get('models')[0]

            form_values = {
                "model_name": model["name"],
                "notes": model["notes"],
                "price_per_prediction": model["price_per_prediction"],
                "data_processing_options": model["preprocessing_steps"]
            }
            
            preprocessing_steps = PreprocessingStep.objects.all()
            form = UploadModelForm(preprocessing_steps=preprocessing_steps, edit_existing=True, initial=form_values)

            context = {
                'form': form,
                'model': model
            }

            return render(request, self.template_name, context=context)
        
    def post(self, request: HttpRequest, model_id=0):
        ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')
        data = dict(request.POST.items())
        
        response = requests.post(f"{ml_service_url}/api/model/edit/{model_id}/", data=data)
        
        if response.status_code == 200:
            messages.success(request, 'Model successfully updated!')
        else:
            messages.error(request, 'Failed to update model. Try again later.')

        return redirect("engineer")
