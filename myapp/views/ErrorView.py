
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

import logging

# Configure logging
logger = logging.getLogger(__name__)

class Error_400(View):
    """
    This class handles HTTP 400 Bad Request errors.

    Attributes:
        template_name (str): The path to the template to render when a 400 error occurs.
    """

    template_name = "errors/400.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles all HTTP request methods and returns a rendered template with a status code of 400.

        Args:
            request (HttpRequest): The incoming HTTP request.
            exception (Exception): The exception that triggered the error.

        Returns:
            HttpResponse: A rendered template with a status code of 400.
        """
        return render(request, self.template_name, {"context": kwargs.get("exception")}, status=400)


class Error_403(View):
    """
    This class handles HTTP 403 Forbidden errors.

    Attributes:
        template_name (str): The path to the template to render when a 403 error occurs.
    """

    template_name = "errors/403.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles all HTTP request methods and returns a rendered template with a status code of 403.

        Args:
            request (HttpRequest): The incoming HTTP request.
            exception (Exception): The exception that triggered the error.

        Returns:
            HttpResponse: A rendered template with a status code of 403.
        """
        return render(request, self.template_name, {"context": kwargs.get("exception")}, status=403)


class Error_404(View):
    """
    This class handles HTTP 404 Not Found errors.

    Attributes:
        template_name (str): The path to the template to render when a 404 error occurs.
    """

    template_name = "errors/404.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles all HTTP request methods and returns a rendered template with a status code of 404.

        Args:
            request (HttpRequest): The incoming HTTP request.
            exception (Exception): The exception that triggered the error.

        Returns:
            HttpResponse: A rendered template with a status code of 404.
        """
        return render(request, self.template_name, {"context": kwargs.get("exception")}, status=404)


class Error_500(View):
    """
    This class handles HTTP 500 Internal Server Error.

    Attributes:
        template_name (str): The path to the template to render when a 500 error occurs.
    """

    template_name = "errors/500.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handles all HTTP request methods and returns a rendered template with a status code of 500.

        Args:
            request (HttpRequest): The incoming HTTP request.
            exception (Exception): The exception that triggered the error.

        Returns:
            HttpResponse: A rendered template with a status code of 500.
        """
        return render(request, self.template_name, {"context": kwargs.get("exception")}, status=500)

