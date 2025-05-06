from django import forms
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import Q, Sum, F
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse

from datetime import datetime
import json
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import traceback

from paypal.standard.forms import PayPalPaymentsForm

from myapp.models import UserProfile, Company, FinanceReport, UploadedRecord
from myapp.utility.SimpleResults import SimpleResult

# Configure logging
logger = logging.getLogger(__name__)

class InvoiceForm(forms.Form):
    INVOICE_TYPE_CHOICES = [
        ('company', 'Company'),
        ('individual', 'Individual'),
    ]

    invoice_type = forms.ChoiceField(
        label="Invoice Type",
        required=True,
        choices=INVOICE_TYPE_CHOICES
    )

    entity = forms.ChoiceField(
        label="Company/Individual",
        required=True
    )

    month = forms.ChoiceField(
        label="Month",
        required=True,
        choices=[(str(i), datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    )

    year = forms.ChoiceField(
        label="Year",
        required=True,
        choices=[(str(y), str(y)) for y in range(datetime.now().year - 5, datetime.now().year + 2)]
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        now = datetime.now()

        invoice_type = self.data.get('invoice_type') or self.initial.get('invoice_type') or 'company'

        if invoice_type == 'individual':
            self.fields['entity'].choices = [
                (profile.user_profile_id, profile.auth_id.get_full_name() or profile.auth_id.username)
                for profile in UserProfile.objects.filter(company_id__isnull=True).select_related('auth_id')
            ]
        else:
            self.fields['entity'].choices = [
                (company.company_id, company.name) for company in Company.objects.all()
            ]

        self.fields['month'].initial = now.month
        self.fields['year'].initial = now.year

@method_decorator([login_required, permission_required("myapp.view_financereport")], name="dispatch")
class FinanceDashboardView(View):
    """
    This class handles the rendering and processing of the finance dashboard.
    """

    template_name = "finance.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        user_profile = UserProfile.objects.get(auth_id=request.user.id)

        invoices = None

        if request.user.is_superuser:
            invoices = FinanceReport.objects.all().order_by('-created_at')
        elif user_profile.company_id is not None:
            invoices = FinanceReport.objects.filter(company_id=user_profile.company_id).order_by('-created_at')
        else:
            invoices = FinanceReport.objects.filter(user_profile_id=user_profile.user_profile_id).order_by('-created_at')

        invoice_form = InvoiceForm()

        num_invoices = invoices.count() if invoices is not None else 0

        if not request.user.is_superuser:
            for invoice in invoices:
                if not invoice.paid:
                    if invoice.cost_incurred == 0:
                        invoice.paid = True
                        invoice.save()
                        continue

                    paypal_dict = {
                        "business": settings.PAYPAL_RECEIVER_EMAIL,
                        "amount": invoice.cost_incurred,
                        "currency_code": "GBP",
                        "item_name": (str(invoice.month) + "/" + str(invoice.year)),
                        "invoice": invoice.finance_report_id,
                        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                        "return": request.build_absolute_uri(reverse("finance_dashboard")),
                        "cancel_return": request.build_absolute_uri(reverse("finance_dashboard")),
                    }
                    invoice.payment_form = PayPalPaymentsForm(initial=paypal_dict)

        context = {
            'num_invoices': num_invoices,
            'invoice_form': invoice_form,
            'is_company_owner': user_profile.is_company_owner,
            'is_admin': request.user.is_superuser,
            'invoices': invoices
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        uploaded_invoice_form = InvoiceForm(request.POST)
        current_user = get_object_or_404(UserProfile, auth_id = self.request.user.id)

        if uploaded_invoice_form.is_valid():
            invoice_type = uploaded_invoice_form.cleaned_data['invoice_type']
            entity_id = uploaded_invoice_form.cleaned_data['entity']
            month = uploaded_invoice_form.cleaned_data['month']
            year = uploaded_invoice_form.cleaned_data['year']

            try:
                generate_invoice(invoice_type, entity_id, month, year, current_user)
            except Exception:
                logger.error(f"An exception occurred while trying to create the invoice for {entity_id}: {traceback.format_exc()}")
                return HttpResponse(content=f"An exception occurred while trying to create the invoice for {entity_id}, please try again later.", status=500)

        else:
            return HttpResponse("Invalid invoice generation submission", status=400)
        
        return redirect("finance_dashboard")

def generate_invoice(invoice_type, entity_id, month, year, user):
    if invoice_type == "company":
        company_obj = Company.objects.filter(company_id=entity_id).first()
        company_users = UserProfile.objects.filter(company_id=entity_id)

        total_cost = UploadedRecord.objects.filter(
            user_id__in=company_users,
            upload_date__year=year,
            upload_date__month=month
            ).aggregate(
                total=Sum(F('model_id__price_per_prediction'))
            )['total'] or 0

        # Placeholder invoice text, this could be formatted for printing as a proper invoice.
        invoice_text = f"Company: {company_obj.name}, (MONTH,YEAR): {(month, year)} costing {total_cost}."

        report = FinanceReport.objects.create(
            company_id=company_obj,
            year=year,
            month=month,
            cost_incurred=total_cost,
            generated_invoice=invoice_text,
            user_id=user,
            created_at=timezone.now()
        )
    elif invoice_type == 'individual':
        user_profile = UserProfile.objects.filter(user_profile_id=entity_id, company_id__isnull=True).select_related('auth_id').first()

        if not user_profile:
            raise ValueError("Invalid individual user selected.")

        total_cost = UploadedRecord.objects.filter(
            user_id=user_profile,
            upload_date__year=year,
            upload_date__month=month
        ).aggregate(
            total=Sum(F('model_id__price_per_prediction'))
        )['total'] or 0

        invoice_text = f"Individual: {user_profile.auth_id.get_full_name() or user_profile.auth_id.username}, (MONTH,YEAR): {(month, year)} costing {total_cost}."

        report = FinanceReport.objects.create(
            user_profile_id=user_profile,
            year=year,
            month=month,
            cost_incurred=total_cost,
            generated_invoice=invoice_text,
            user_id=user,
            created_at=timezone.now()
        )

    return report

def download_invoice(request, invoice_id):
    try:
        invoice = get_object_or_404(FinanceReport, finance_report_id=invoice_id)
        invoice_content = invoice.generated_invoice

        response = HttpResponse(content_type='application/pdf', status=200)
        response['Content-Disposition'] = f"attachment; filename=invoice_{invoice_id}.pdf"

        p = canvas.Canvas(response, pagesize=letter)
        _, height = letter

        p.drawString(10, height-10, invoice_content)
        p.showPage()
        p.save()

        return response
    except Exception:
        logger.error(f"Failed to download invoice {invoice_id}, error: {traceback.format_exc()}")
        return HttpResponse(content=f"Failed to download invoice {invoice_id}, please try again later.", status=400)

def load_entity_field(request: HttpRequest):
    invoice_type = request.GET.get("invoice_type", "company")
    form = InvoiceForm(initial={"invoice_type": invoice_type})

    entity_field = form["entity"]
    select_html = entity_field.as_widget(attrs={"class": "form-select"})
    label_text = "Individual To Invoice" if invoice_type == "individual" else "Company To Invoice"

    return JsonResponse({
        "select_html": select_html,
        "label": label_text,
    })

@method_decorator([login_required, permission_required("myapp.view_financereport")], name="dispatch")   
class CompanyDetailsView(View):
    """
    This class handles the rendering and processing of the company details page.
    """
    
    template_name = "company_details.html"
    
    def get(self, request: HttpRequest) -> HttpResponse:
        return self.__render_company_details_page(request, SimpleResult())
    
    def post(self, request: HttpRequest) -> HttpResponse:
        result = SimpleResult()
        
        company_name = request.POST.get('companyName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        user_profile = UserProfile.objects.get(auth_id=request.user.id)
        company = user_profile.company_id
        contact_info = company.contact_info_id
        
        # Update info if it was provided
        company.name = company_name if company_name else company.name
        contact_info.email = email if email else contact_info.email
        contact_info.phone = phone if phone else contact_info.phone
        contact_info.address = address if address else contact_info.address
        
        company.save()
        contact_info.save()
        
        result.add_info_message("Contact details saved successfully")
        
        return self.__render_company_details_page(request, result)
    
    def __render_company_details_page(self, request, result: SimpleResult) -> HttpResponse:    
        user_profile = UserProfile.objects.get(auth_id=request.user.id)
        
        # Page only available for the company owner
        if not user_profile.is_company_owner:
            return redirect("index")
        
        company = user_profile.company_id
        company_contact_info = company.contact_info_id
        
        context = {
            "company_name": company.name,
            "current_email": company_contact_info.email,
            "current_phone": company_contact_info.phone,
            "current_address": company_contact_info.address,
            'info_messages': result.get_info_messages(),
            'error_messages': result.get_error_messages()
        }
        
        return render(request, self.template_name, context=context)


@method_decorator([login_required, permission_required("myapp.view_financereport")], name="dispatch")
class CompanyManageEmployeesView(View):
    """
    This class handles the rendering and processing of the add employees page.
    """
    
    template_name = "company_manage_users.html"
    
    def get(self, request: HttpRequest) -> HttpResponse:
        return self.__render_company_details_page(request, SimpleResult())
    
    def post(self, request: HttpRequest) -> JsonResponse:
        requestUser = UserProfile.objects.get(auth_id=request.user.id)
        
        data = json.loads(request.body.decode('utf-8'))
        user_id = data['user']
        action = data['action']
        
        user = UserProfile.objects.get(user_profile_id=user_id)
        
        if action == "remove":
            user.company_id = None
        
        elif action == "add":
            user.company_id = requestUser.company_id
            
        user.save()
        
        return JsonResponse({
                'status': 'success',
            })
        
    
    def __render_company_details_page(self, request, result: SimpleResult) -> HttpResponse:    
        user_profile = UserProfile.objects.get(auth_id=request.user.id)
        
        # Page only available for the company owner
        if not user_profile.is_company_owner:
            return redirect("index")
        
        company = user_profile.company_id
        users_in_company = UserProfile.objects.filter(~Q(user_profile_id=user_profile.pk), company_id=company)
        users_without_company = UserProfile.objects.filter(company_id=None)

        context = {
            'users_in_company': users_in_company,
            'users_without_company': users_without_company,
            'info_messages': result.get_info_messages(),
            'error_messages': result.get_error_messages()
        }
        
        return render(request, self.template_name, context=context)
