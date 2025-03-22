from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

import logging

from myapp.models import UserProfile
from myapp.utility.SimpleResults import SimpleResult, Message

# Configure logging
logger = logging.getLogger(__name__)

class AccountCreationView(View):
    """
    This class handles the rendering and processing of the account creation page.
    """

    template_name = "registration/account_creation.html"

    def get(self, request: HttpRequest) -> HttpResponse: 
        # Kick out any user that is already logged in  
        if request.user.is_authenticated:
            return redirect("index")
            
        return self.__render_account_creation_page(request, None)

    def post(self, request: HttpRequest) -> HttpResponse:
        # Kick out any user that is already logged in    
        if request.user.is_authenticated:
            return redirect("index")
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        userType = request.POST.get('userType')
        
        result = UserProfile.create_account(username, email, password, userType)
        
        # If successful, log them in with their provided credentials
        if result.success:
            userProfile: UserProfile = result.payload
            login(request, userProfile.auth_id)
            return redirect("index")
            
        # If unsuccessful, return the user to the account creation page 
        return self.__render_account_creation_page(request, result.get_error_messages())

    def __render_account_creation_page(self, request, error_messages: list[Message]) -> HttpResponse:
        # Admin should not be a selectable user type
        user_groups = Group.objects.filter(~Q(id=UserProfile.GroupIDs.ADMINISTRATOR_ID))
        
        context = {
            'user_groups': user_groups,
            'error_messages': error_messages
        }
        
        return render(request, self.template_name, context=context)
    
    
@method_decorator(login_required, name="dispatch")
class AccountContactDetailsView(View):
    """
    This class handles the rendering and processing of the contact details page.
    """
    
    template_name = "contact_details.html"
    
    def get(self, request: HttpRequest) -> HttpResponse: 
        return self.__render_contact_details_page(request, SimpleResult())
    
    def post(self, request: HttpRequest) -> HttpResponse:
        result = SimpleResult()
        
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        user_profile = UserProfile.objects.get(auth_id=request.user.id)
        contact_info = user_profile.contact_info_id
        
        # Update info if it was provided
        contact_info.email = email if email else contact_info.email
        contact_info.phone = phone if phone else contact_info.phone
        contact_info.address = address if address else contact_info.address
        
        contact_info.save()
        result.add_info_message("Contact details saved successfully")
        
        return self.__render_contact_details_page(request, result)
    
    def __render_contact_details_page(self, request, result: SimpleResult) -> HttpResponse:
        user_profile = UserProfile.objects.get(auth_id=request.user.id)
        contact_info = user_profile.contact_info_id
        
        context = {
            "current_email": contact_info.email,
            "current_phone": contact_info.phone,
            "current_address": contact_info.address,
            'info_messages': result.get_info_messages(),
            'error_messages': result.get_error_messages()
        }
        
        return render(request, self.template_name, context=context)
