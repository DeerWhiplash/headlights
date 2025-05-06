from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import Claim, Feedback, DatabaseLog, PredictionModel, OperationLookup, TableLookup, TrainingDataset, UploadedRecord, UserProfile, Company, ContactInfo, FinanceReport

#remove admin form validation so these dont block saves
User._meta.get_field("username").validators.pop(0)
User._meta.get_field("email").validators.pop(0)

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].validators.pop(0)

form = CustomUserChangeForm()
UserAdmin.form = CustomUserChangeForm

UserAdmin.list_display = list(UserAdmin.list_display) + ["is_active"]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_id', 'settlement_value', 'accident_type', 'injury_prognosis', 'special_health_expenses', 'special_reduction', 'special_overage', 'general_rest', 'special_additional_injury', 'special_earnings_loss', 'special_usage_loss', 'special_medications', 'special_asset_damage', 'special_rehabilitation', 'special_fixes', 'general_fixed', 'general_uplift', 'special_loaner_vehicle', 'special_trip_costs', 'special_journey_expenses', 'special_therapy', 'exceptional_circumstances', 'minor_psychological_injury', 'dominant_injury', 'whiplash', 'vehicle_type', 'weather_conditions', 'accident_date', 'claim_date', 'vehicle_age', 'driver_age', 'number_of_passengers', 'accident_description', 'injury_description', 'police_report_filed', 'witness_present', 'gender')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_id', 'user_id', 'rating', 'notes')

@admin.register(DatabaseLog)
class LogAdmin(admin.ModelAdmin):
    list_display = ('database_log_id', 'log_time', 'user_id', 'affected_table_id', 'operation_performed', 'successful', 'notes')

@admin.register(PredictionModel)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('model_id', 'model_name', 'notes', 'filepath', 'price_per_prediction')

@admin.register(OperationLookup)
class OperationLookupAdmin(admin.ModelAdmin):
    list_display = ('operation_id', 'operation_name')

@admin.register(TableLookup)
class TableLookupAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'table_name')

@admin.register(TrainingDataset)
class TrainingDatasetAdmin(admin.ModelAdmin):
    list_display = ('training_dataset_id', 'claim_id')

@admin.register(UploadedRecord)
class UploadedRecordAdmin(admin.ModelAdmin):
    list_display = ('uploaded_record_id', 'user_id', 'claim_id', 'feedback_id', 'model_id', 'predicted_settlement', 'upload_date')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_profile_id', 'auth_id', 'contact_info_id', 'company_id')
    
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'contact_info_id', 'name')
    
@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('contact_info_id', 'phone', 'email', 'address')
    
@admin.register(FinanceReport)
class FinanceReportAdmin(admin.ModelAdmin):
    list_display = ('finance_report_id', 'user_id', 'year', 'month', 'cost_incurred', 'generated_invoice')
    
