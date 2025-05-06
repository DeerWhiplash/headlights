from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.generic import BSModalCreateView

import logging
import requests
import pandas as pd

from myapp.models import Claim, UploadedRecord, Feedback, UserProfile, PredictionModel, TrainingDataset
from myapp.utility.SimpleResults import SimpleResultWithPayload

# Configure logging
logger = logging.getLogger(__name__)
class UploadedClaimsForm(forms.Form):
    uploaded_claims = forms.ModelChoiceField(
        queryset=Claim.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'style': 'width: 100%; padding: 0.5rem; font-size: 1rem;'
            }
        ),
        empty_label="Select a claim..."
    )

    model = forms.ModelChoiceField(
        queryset = PredictionModel.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-select',
                'style': 'width: 100%; padding: 0.5rem; font-size: 1rem;'
            }
        ),
        empty_label="Select a prediction model..."
    )

class SettlementForm(forms.Form):
    user_settlement = forms.DecimalField(
        label="Your Settlement Decision (£)",
        max_digits=10, decimal_places=2,
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'step': 'any',
                'inputmode': 'decimal',
            }),
    )

    def __init__(self, *args, **kwargs):
        predicted_settlement = kwargs.pop('predicted_settlement', None)

        super().__init__(*args, **kwargs)

        if predicted_settlement is not None:
            self.fields['user_settlement'].initial = round(predicted_settlement)

class FeedbackForm(BSModalModelForm):
    rating_choices = [(i, str(i)) for i in range(1, 6)] # 1 to 5 rating choices

    rating = forms.ChoiceField(choices=rating_choices, required=True)
    notes = forms.CharField(widget=forms.Textarea, max_length=Feedback._meta.get_field('notes').max_length,
                            label="Feedback Notes", required=False)

    class Meta:
        model = Feedback
        fields = ['rating', 'notes']

def create_uploaded_record(record: dict) -> UploadedRecord:

    try:
        required_keys = {'user', 'claim', 'prediction', 'model_id'}
        if not all(key in record for key in required_keys):
            missing_keys = required_keys - record.keys()
            raise ValueError(f"Missing required keys in record: {missing_keys}")
        
        uploaded_record = UploadedRecord.objects.create(
                        user_id = record['user'],
                        claim_id = record['claim'],
                        predicted_settlement = record['prediction'],
                        model_id = record['model_id'],
                        upload_date = timezone.now()
        )
        uploaded_record.save()

        return uploaded_record

    except ValueError as e:
        logger.error("Invalid input data for UploadedRecord: %s", str(e))
        raise
    except Exception as e:
        logger.exception("Unexpected error while creating UploadedRecord")
        raise RuntimeError("An unexpected error occurred while saving the record") from e

def get_claim_prediction(claim, model):
    """
    This function gets the prediction result for a claim, and creates an UploadedRecord object.

    Args:
        claim: the claim object.
        model: the model object

    Returns:
        UploadedRecord: the uploaded record object.
    """

    model_id = model.model_id
    claim_data = model_to_dict(claim)
    claim_data.pop('claim_id', None)

    ml_service_url = getattr(settings, 'ML_SERVICE_URL', 'http://ml-service:8001')

    try:
        response = requests.post(
        f"{ml_service_url}/api/model/predict/", 
        json={'model_id': model_id, 'data': claim_data},
        timeout=10)

        # raises an exception for http errors
        response.raise_for_status()
    
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            logger.exception("Failed to parse JSON response from ML service")
            raise ValueError("Invalid JSON response from ML service")
        
        if (not isinstance(response_data, dict)) or ('data' not in response_data):
            logger.error("Unexpected response format: %s", response_data)
            raise ValueError("ML service response format is invalid")
        
        if 'prediction' not in response_data['data']:
            logger.error("Prediction key missing in response: %s", response_data)
            raise ValueError("Prediction key missing from ML response")
        
        return response_data['data']['prediction']
        
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to fetch prediction from ML service")
        raise ConnectionError("Error connecting to ML service") from e
    

@method_decorator(login_required, name="dispatch")
class CustomerDashboardView(View):
    """
    This class handles the rendering and processing of the end-user dashboard page.
    """

    template_name = "customer.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the GET request for the customer dashboard.

        Args:
            request: the GET request object.

        Returns:
            render: the customer.html template.
        """
        current_user = get_object_or_404(UserProfile, auth_id = self.request.user.id)
        user_uploaded_records = UploadedRecord.objects.filter(user_id=current_user)

        num_claims = Claim.objects.all().count()
        uploaded_claims_form = UploadedClaimsForm()
        settlement_form = SettlementForm()

        uploaded_record_id = request.session.get('uploaded_record_id', None)
        uploaded_record = None
        if uploaded_record_id:
            try:
                uploaded_record = UploadedRecord.objects.get(uploaded_record_id=uploaded_record_id)
            except UploadedRecord.DoesNotExist:
                uploaded_record = None
                # Remove invalid session key
                del request.session['uploaded_record_id']

        if uploaded_record and isinstance(uploaded_record.predicted_settlement, (int, float)):
            settlement_form = SettlementForm(None, predicted_settlement=uploaded_record.predicted_settlement)

            uploaded_record.predicted_range = {
                'center': round(uploaded_record.predicted_settlement, 2),
                'lower': round(uploaded_record.predicted_settlement * 0.95, 2),
                'upper': round(uploaded_record.predicted_settlement * 1.05, 2)
            }

        context = {
            'num_claims': num_claims,
            'uploaded_claims_form': uploaded_claims_form,
            'user_uploaded_records': user_uploaded_records,
            'uploaded_record': uploaded_record,
            'settlement_form': settlement_form,
        }

        logger.info(f"{request.user} accessed the customer dashboard.")
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        """
        Handles the POST request for the customer dashboard.

        Submits the uploaded claims form, and returns the prediction result from the prediction API.

        Args:
            request: the POST request object.

        Returns:
            HttpResponseRedirect: the customer dashboard page, with the prediction result.

        """
        uploaded_claim_form = UploadedClaimsForm(request.POST)
        current_user = get_object_or_404(UserProfile, auth_id = self.request.user.id)

        if 'uploaded_claims' in request.POST:
            if uploaded_claim_form.is_valid():
                selected_claim = uploaded_claim_form.cleaned_data['uploaded_claims']
                selected_model = uploaded_claim_form.cleaned_data['model']

                predicted_settlement = get_claim_prediction(selected_claim, selected_model)

                if predicted_settlement is not None:
                    uploaded_record = create_uploaded_record({
                        'user': current_user,
                        'claim': selected_claim,
                        'model_id': selected_model,
                        'prediction': predicted_settlement,
                        })
                    request.session['uploaded_record_id'] = uploaded_record.uploaded_record_id

                else:
                    return HttpResponseBadRequest(JsonResponse({"error": "Prediction value is missing"}))
            else:
                return HttpResponse("Invalid uploaded claims form submission", status=400)

        if 'user_settlement' in request.POST:
            uploaded_record_id = request.session.get('uploaded_record_id')
            if uploaded_record_id:
                uploaded_record = get_object_or_404(UploadedRecord, uploaded_record_id=uploaded_record_id)
                settlement_form = SettlementForm(request.POST)

                if settlement_form.is_valid():
                    uploaded_record.user_settlement = settlement_form.cleaned_data['user_settlement']
                    uploaded_record.save()
                else:
                    return HttpResponse("Invalid settlement form submission", status=400)
            else:
                return HttpResponse("No uploaded record found in session", status=400)

        return redirect("customer_dashboard")

@method_decorator(login_required, name="dispatch")
class ClaimUploadView(View):
    """
    This class handles the processing of uploaded claims data.
    """
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        return redirect("customer_dashboard")
    
    def post(self, request: HttpRequest, ignore_validation: int = 0) -> JsonResponse:
        result = SimpleResultWithPayload()
        file = request.FILES['claims_file']
        preprocess = request.POST.get('preprocess')
        add_to_training_data = request.POST.get('trainingData')
        
        if not file.name.endswith(".csv"):
            result.add_error_message_and_mark_unsuccessful("Invalid file type")
        
        if result.success:
            upload_result = UploadedRecord.upload_claims_from_file(file, None, True if ignore_validation == 1 else False, preprocess)  
            result.add_messages_from_result_and_mark_unsuccessful_if_error_found(upload_result)
            result.payload = upload_result.payload
            
        if result.success and add_to_training_data:
            claims = [uploaded_record.claim_id for uploaded_record in result.payload]
            training_data_result = TrainingDataset.add_claims_to_training_data(claims)
            result.add_messages_from_result_and_mark_unsuccessful_if_error_found(training_data_result)
            
        status = "success"
        if not result.success:
            status = "error"
            for message in result.get_error_messages():
                if message.text == "Column Name Error":
                    status = "confirmationRequired"
                    result.messages.remove(message)
        
        return JsonResponse({
                'status': status,
                'message': '\n\n'.join([message.text for message in result.messages])
            })


@method_decorator(login_required, name="dispatch")
class ProcessClaimsFileView(View):
    """
    This class handles applying preprocessing to customer claim files.
    """
    
    template_name = "claims_preprocessing.html"
    
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        return render(request, self.template_name)

    def post(self, request: HttpRequest, ignore_validation: int = 0):
        result = SimpleResultWithPayload()
        file = request.FILES['claims_file']
        
        if not file.name.endswith(".csv"):
            result.add_error_message_and_mark_unsuccessful("Invalid file type")
        
        if result.success:
            df = pd.read_csv(file)
            upload_result = Claim.apply_preprocessing(df, True if ignore_validation == 1 else False)  
            result.add_messages_from_result_and_mark_unsuccessful_if_error_found(upload_result)
            result.payload = upload_result.payload
            
        status = "success"
        if not result.success:
            status = "error"
            for message in result.get_error_messages():
                if message.text == "Column Name Error":
                    status = "confirmationRequired"
                    result.messages.remove(message)
        
        if status != "success":
            context = {
                "status": status,
                "messages": result.get_error_messages()
            }
            return render(request, self.template_name, context)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=ProcessedClaims.csv'
        result.payload.to_csv(response, index=False)
        
        return response


@method_decorator(login_required, name="dispatch")
class PredictionFeedbackView(BSModalCreateView):
    """
    This class handles the processing of prediction feedback data.
    """
    template_name = "forms/prediction_feedback_form.html"
    form_class = FeedbackForm
    success_message = 'Success: Feedback submitted.'
    success_url = reverse_lazy('customer_dashboard')

    def form_valid(self, form):
        """
        Handles the form validation for the prediction feedback form.

        Assigns the request user_id to the feedback form, and assigns the feedback to the uploaded record.

        Args:
            form: the feedback form.

        Returns:
            super().form_valid(form): the feedback form.
        """
        user_profile = get_object_or_404(UserProfile, auth_id=self.request.user.id)

        # Save the feedback form instance first
        feedback_instance = form.instance
        feedback_instance.user_id = user_profile
        feedback_instance.save()

        # Retrieve the uploaded_record_id from the session, and assign the feedback to the uploaded record
        uploaded_record_id = self.request.session.get('uploaded_record_id', None)
        if uploaded_record_id:
            uploaded_record = get_object_or_404(UploadedRecord, uploaded_record_id=uploaded_record_id)
            uploaded_record.feedback_id = feedback_instance
            uploaded_record.save()

            # Clear the uploaded_record_id from the session after feedback is submitted
            del self.request.session['uploaded_record_id']

        return super().form_valid(form)
