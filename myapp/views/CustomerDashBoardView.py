from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect,JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

import logging

from myapp.models import Claim, UploadedRecord

# Configure logging
logger = logging.getLogger(__name__)

@method_decorator(login_required, name="dispatch")
class CustomerDashboardView(View):
    """
    This class handles the rendering and proccessing of the end-user dashboard page.
    """

    template_name = "customer.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the GET request for the customer dashboard.

        Args:
            request: the GET request object.
            message: 

        Returns:
            render: the customer.html template.
        """

        num_claims = Claim.objects.all().count()
        
        context = {
            'num_claims': num_claims,
        }

        logger.info(f"{request.user} accessed the customer dashboard.")
        return render(request, self.template_name, context=context)

@method_decorator(login_required, name="dispatch")
class ClaimUploadView(View):
    """
    This class handles the proccessing of uploaded claims data.
    """
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        return redirect("./")
    
    def post(self, request: HttpRequest) -> JsonResponse:
        file = request.FILES['claims_file']  
        result = UploadedRecord.upload_claims_from_file(file, None)  
        
        return JsonResponse({
                'status': 'success' if result.success else "error",
                'message': '\n'.join([message.text for message in result.messages])
            })