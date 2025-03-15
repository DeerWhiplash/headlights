from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse

import logging

from myapp.models import Claim

# Configure logging
logger = logging.getLogger(__name__)


class IndexView(View):
    """
    This class handles the rendering and proccessing of the index page.
    """

    template_name = "index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the GET request for the index page.

        Args:
            request: the GET request object.

        Returns:
            render: the index.html template.
        """

        num_claims = Claim.objects.all().count()
        
        context = {
            'num_claims': num_claims,
        }

        logger.info(f"{request.user} accessed the index page.")
        return render(request, self.template_name, context=context)
    