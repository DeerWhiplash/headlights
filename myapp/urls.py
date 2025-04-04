"""
URL configuration for desd project.
"""
from django.urls import path

from myapp.views.CustomerDashBoardView import CustomerDashboardView, ClaimUploadView, PredictionFeedbackView
from myapp.views.IndexView import IndexView
from myapp.views.MLDashboardView import MLDashboardView, UploadModelView
from myapp.views.AccountManagementView import AccountCreationView, AccountContactDetailsView
from myapp.views.FinanceDashboardViews import FinanceDashboardView, CompanyDetailsView, CompanyManageEmployeesView


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("ml/", MLDashboardView.as_view() , name="ml_dashboard"),
    
    # Customer dashboard URLs
    path("customer/", CustomerDashboardView.as_view(), name="customer_dashboard"),  
    path("customer/record-upload/", ClaimUploadView.as_view(), name="upload_claims"),
    path("customer/record-upload/<int:ignore_validation>/", ClaimUploadView.as_view(), name="upload_claims"),
    path("customer/prediction-feedback/", PredictionFeedbackView.as_view(), name="prediction_feedback"),
    
    # Account management URLs
    path("account/create/", AccountCreationView.as_view(), name="account_creation"),
    path("account/contact-details/", AccountContactDetailsView.as_view(), name="contact_details"),
    
    # Finance URLs
    path("finance/", FinanceDashboardView.as_view(), name="finance_dashboard"),
    path("finance/company-details/", CompanyDetailsView.as_view(), name="company_details"),
    path("finance/manage-employees/", CompanyManageEmployeesView.as_view(), name="company_manage_employees"),
    
    # ML-related API endpoints
    path("api/upload-model/", UploadModelView.as_view(), name="upload_model"),
    # Additional endpoints could be added here as needed
]
