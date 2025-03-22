# This is an auto-generated Django model module.

# Remember to migrate to the database using the following:
#   manage.py makemigrations <app_name>
#   manage.py migrate <app_name>

# If this doesn't work you may need to reset your migrations
#   delete all files in the migrations folder except __init__.py
#   run python manage.py migrate --fake <app_name> zero

# Changes made to the database can turned into models using the following:
#   python manage.py inspectdb > models.py

from django.contrib.auth.models import User, Group
from django.db import models, transaction
from datetime import date
from .utility.SimpleResults import SimpleResult, SimpleResultWithPayload
from .utility import CaseConversion
import pandas as pd

import logging
logger = logging.getLogger(__name__)

class Claim(models.Model):
    claim_id = models.AutoField(db_column='ClaimID', primary_key=True)  
    settlement_value = models.FloatField(db_column='SettlementValue', blank=True, null=True)  
    accident_type = models.CharField(db_column='AccidentType', max_length=255, blank=True, null=True)  
    injury_prognosis = models.IntegerField(db_column='InjuryPrognosis', blank=True, null=True)  
    special_health_expenses = models.FloatField(db_column='SpecialHealthExpenses', blank=True, null=True)  
    special_reduction = models.FloatField(db_column='SpecialReduction', blank=True, null=True)  
    special_overage = models.FloatField(db_column='SpecialOverage', blank=True, null=True)  
    general_rest = models.FloatField(db_column='GeneralRest', blank=True, null=True)  
    special_additional_injury = models.FloatField(db_column='SpecialAdditionalInjury', blank=True, null=True)  
    special_earnings_loss = models.FloatField(db_column='SpecialEarningsLoss', blank=True, null=True)  
    special_usage_loss = models.FloatField(db_column='SpecialUsageLoss', blank=True, null=True)  
    special_medications = models.FloatField(db_column='SpecialMedications', blank=True, null=True)  
    special_asset_damage = models.FloatField(db_column='SpecialAssetDamage', blank=True, null=True)  
    special_rehabilitation = models.FloatField(db_column='SpecialRehabilitation', blank=True, null=True)  
    special_fixes = models.FloatField(db_column='SpecialFixes', blank=True, null=True)  
    general_fixed = models.FloatField(db_column='GeneralFixed', blank=True, null=True)  
    general_uplift = models.FloatField(db_column='GeneralUplift', blank=True, null=True)  
    special_loaner_vehicle = models.FloatField(db_column='SpecialLoanerVehicle', blank=True, null=True)  
    special_trip_costs = models.FloatField(db_column='SpecialTripCosts', blank=True, null=True)  
    special_journey_expenses = models.FloatField(db_column='SpecialJourneyExpenses', blank=True, null=True)  
    special_therapy = models.FloatField(db_column='SpecialTherapy', blank=True, null=True)  
    exceptional_circumstances = models.IntegerField(db_column='ExceptionalCircumstances', blank=True, null=True)  
    minor_psychological_injury = models.IntegerField(db_column='MinorPsychologicalInjury', blank=True, null=True)  
    dominant_injury = models.CharField(db_column='DominantInjury', max_length=255, blank=True, null=True)  
    whiplash = models.IntegerField(db_column='Whiplash', blank=True, null=True)  
    vehicle_type = models.CharField(db_column='VehicleType', max_length=255, blank=True, null=True)  
    weather_conditions = models.CharField(db_column='WeatherConditions', max_length=255, blank=True, null=True)  
    accident_date = models.IntegerField(db_column='AccidentDate', blank=True, null=True)  
    claim_date = models.IntegerField(db_column='ClaimDate', blank=True, null=True)  
    vehicle_age = models.IntegerField(db_column='VehicleAge', blank=True, null=True)  
    driver_age = models.IntegerField(db_column='DriverAge', blank=True, null=True)  
    number_of_passengers = models.IntegerField(db_column='NumberOfPassengers', blank=True, null=True)  
    accident_description = models.CharField(db_column='AccidentDescription', max_length=255, blank=True, null=True)  
    injury_description = models.CharField(db_column='InjuryDescription', max_length=255, blank=True, null=True)  
    police_report_filed = models.IntegerField(db_column='PoliceReportFiled', blank=True, null=True)  
    witness_present = models.IntegerField(db_column='WitnessPresent', blank=True, null=True)  
    gender = models.CharField(db_column='Gender', max_length=255, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'Claim'

    def __str__(self) -> str:
        """
        This function returns a Claim in a neat string format.
        """
        return f"""{self.settlement_value} | {self.accident_type} | {self.injury_prognosis} | {self.special_health_expenses} |
                 {self.special_reduction} | {self.special_overage} | {self.general_rest} | {self.special_additional_injury} |
                 {self.special_earnings_loss} | {self.special_usage_loss} | {self.special_medications} | {self.special_asset_damage} |
                 {self.special_rehabilitation} | {self.special_fixes} | {self.general_fixed} | {self.general_uplift} | {self.special_loaner_vehicle} |
                 {self.special_trip_costs} | {self.special_journey_expenses} | {self.special_therapy} | {self.exceptional_circumstances} | {self.minor_psychological_injury} |
                 {self.dominant_injury} | {self.whiplash} | {self.vehicle_type} | {self.weather_conditions} | {self.accident_date} | {self.claim_date} | {self.vehicle_age} |
                 {self.driver_age} | {self.number_of_passengers} | {self.accident_description} | {self.injury_description} | {self.police_report_filed} | {self.witness_present} | {self.gender}"""
    
    def create_claim_from_series(datarow: pd.Series):
        claim = Claim()  
        for key, value in datarow.items():  
            snake_key = CaseConversion.to_snake(key)
            if hasattr(claim, snake_key):  
                setattr(claim, snake_key, value)  
        
        return claim
    
    @staticmethod
    def create_claims_from_dataframe(df: pd.DataFrame) -> list:
        claims = []
        for index, datarow in df.iterrows():
            claims.append(Claim.create_claim_from_series(datarow))
            
        return claims
    
    @staticmethod
    def validate_columns(df: pd.DataFrame) -> SimpleResult:
        result = SimpleResult()
        
        attributes = Claim._meta.get_fields()
        db_column_names = []
        for attr in attributes:
            if hasattr(attr, 'db_column'):
                db_column_names.append(attr.db_column)
        db_column_names.pop(0) # Remove the primary key
        
        csv_columns = df.columns

        excess_columns = []
        for column in csv_columns:
            pascal_column = CaseConversion.to_pascal(column)
            if pascal_column in db_column_names:
                db_column_names.remove(pascal_column)
            else:
                excess_columns.append(column)
                
        missing_columns = db_column_names[:]

        if len(missing_columns) > 0 :
            result.add_error_message_and_mark_unsuccessful(f"The following columns could not be found in the uploaded file: {', '.join(missing_columns)}")
            
        if len(excess_columns) > 0:
            result.add_error_message_and_mark_unsuccessful(f"The following columns are either missnamed or invalid: {', '.join(excess_columns)}")
            
        if len(missing_columns) > 0 or len(excess_columns) > 0:
            result.add_error_message("Column Name Error")
            
        return result


class ContactInfo(models.Model):
    contact_info_id = models.AutoField(db_column='ContactInfoID', primary_key=True)
    phone = models.CharField(db_column='Phone', max_length=255, blank=True, null=True)
    email = models.CharField(db_column='Email', max_length=255, blank=True, null=True)
    address = models.CharField(db_column='Address', max_length=255, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'ContactInfo'

    def __str__(self) -> str:
        """
        This function returns ContactInfo in a neat string format.
        """
        return f"{self.email} | {self.phone} | {self.address}"
    

class Company(models.Model):
    company_id = models.AutoField(db_column='CompanyID', primary_key=True)
    contact_info_id = models.ForeignKey(ContactInfo, models.PROTECT, db_column='ContactInfoID', blank=True, null=True)
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'Company'

    def __str__(self) -> str:
        """
        This function returns a Company in a neat string format.
        """
        return f"{self.name} | {self.contact_info_id}"
    

class UserProfile(models.Model):
    user_profile_id = models.AutoField(db_column='UserProfileID', primary_key=True)
    auth_id = models.ForeignKey(User, models.PROTECT, db_column='AuthID', blank=True, null=True)
    contact_info_id = models.ForeignKey(ContactInfo, models.PROTECT, db_column='ContactInfoID', blank=True, null=True)
    company_id = models.ForeignKey(Company, models.PROTECT, db_column='CompanyID', blank=True, null=True)
    
    class GroupIDs():
        """
        Used to more easily keep track of user group IDs instead of leaving random numbers all over the codebase
        """
        END_USER_ID = 1
        ENGINEER_ID = 2
        ADMINISTRATOR_ID = 3
        FINANCE_ID = 4
    
    class Meta:
        managed = True
        db_table = 'UserProfile'

    def __str__(self) -> str:
        """
        This function returns a UserProfile in a neat string format.
        """
        return f"{self.auth_id} | {self.contact_info_id} | {self.company_id}"
    
    @staticmethod
    def validate_unique_username(username: str) -> SimpleResult:
        result = SimpleResult()
        
        if User.objects.filter(username=username).exists():
            result.add_error_message_and_mark_unsuccessful("Username already exists")
            
        return result
    
    @staticmethod
    def create_account(username: str, email: str, password: str, groupID: int, 
                       address: str=None, phone: str=None, company: Company=None
                       ) -> SimpleResultWithPayload:   
        result = SimpleResultWithPayload()
        
        result.add_messages_from_result_and_mark_unsuccessful_if_error_found(UserProfile.validate_unique_username(username))
        if not result.success:
            return result
        
        with transaction.atomic():
            newUserAuth = User.objects.create_user(username=username, email=email, password=password)
            
            # All users should have end user/customer permissions
            endUserGroup = Group.objects.get(id=UserProfile.GroupIDs.END_USER_ID)
            newUserAuth.groups.add(endUserGroup)
            
            # Add the selected user group if it wasn't end user
            if groupID != UserProfile.GroupIDs.END_USER_ID:
                group = Group.objects.get(id=groupID)
                newUserAuth.groups.add(group)
                
            # Populate user contact info
            contactInfo = ContactInfo()
            contactInfo.email = email
            contactInfo.address = address
            contactInfo.phone = phone
            
            # Populate all user profile fields
            newUserProfile = UserProfile()
            newUserProfile.auth_id = newUserAuth
            newUserProfile.contact_info_id = contactInfo
            newUserProfile.company_id = company
            
            # Save all new objects
            newUserAuth.save()
            contactInfo.save()
            if company:
                company.save()
            newUserProfile.save()
        
        result.payload = newUserProfile
        
        return result


class FinanceReport(models.Model):
    finance_report_id = models.AutoField(db_column='FinanceReportID', primary_key=True)
    user_id = models.ForeignKey(UserProfile, models.PROTECT, db_column='UserID', blank=True, null=True) 
    year = models.IntegerField(db_column='Year', blank=True, null=True)  
    month = models.IntegerField(db_column='Month', blank=True, null=True)
    cost_incurred = models.FloatField(db_column='CostIncurred', blank=True, null=True)
    generated_invoice = models.CharField(db_column='GeneratedInvoice', max_length=255, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'FinanceReport'

    def __str__(self) -> str:
        """
        This function returns a FinanceReport in a neat string format.
        """
        return f"{self.year} | {self.month} | {self.cost_incurred} | {self.generated_invoice}"


class Feedback(models.Model):
    feedback_id = models.AutoField(db_column='FeedbackID', primary_key=True)  
    user_id = models.ForeignKey(UserProfile, models.PROTECT, db_column='UserID', blank=True, null=True)  
    rating = models.IntegerField(db_column='Rating', blank=True, null=True)  
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'Feedback'

    def __str__(self) -> str:
        """
        This function returns Feedback in a neat string format.
        """
        return f"{self.rating} | {self.notes}"


class DatabaseLog(models.Model):
    database_log_id = models.AutoField(db_column='DatabaseLogID', primary_key=True)  
    log_time = models.DateTimeField(db_column='LogTime', blank=True, null=True)  
    user_id = models.ForeignKey(UserProfile, models.PROTECT, db_column='UserID', blank=True, null=True)  
    affected_table_id = models.ForeignKey('TableLookup', models.PROTECT, db_column='AffectedTableID', blank=True, null=True)  
    operation_performed = models.ForeignKey('OperationLookup', models.PROTECT, db_column='OperationPerformed', blank=True, null=True)  
    successful = models.BooleanField(db_column='Successful', blank=True, null=True)  
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'DatabaseLog'

    def __str__(self) -> str:
        """
        This function returns a DatabaseLog in a neat string format.
        """
        return f"{self.log_time} | {self.user_id} | {self.affected_table_id} | {self.operation_performed} | {self.successful} | {self.notes}"


class PredictionModel(models.Model):
    model_id = models.AutoField(db_column='ModelID', primary_key=True)  
    model_name = models.CharField(db_column='ModelName', max_length=255, blank=True, null=True)
    model_type = models.CharField(db_column='ModelType', max_length=255, blank=True, null=True)
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  
    filepath = models.CharField(db_column='FilePath', max_length=255, blank=True, null=True)  
    price_per_prediction = models.FloatField(db_column='PricePerPrediction', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'PredictionModel'

    def __str__(self) -> str:
        """
        This function returns a PredictionModel in a neat string format.
        """
        return f"{self.model_name} | {self.notes} | {self.filepath} | {self.price_per_prediction}"


class OperationLookup(models.Model):
    operation_id = models.AutoField(db_column='OperationID', primary_key=True)  
    operation_name = models.CharField(db_column='OperationName', max_length=255, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'OperationLookup'

    def __str__(self) -> str:
        """
        This function returns an OperationLookup in a neat string format.
        """
        return f"{self.operation_name}"
    
    
class TableLookup(models.Model):
    table_id = models.AutoField(db_column='TableID', primary_key=True) 
    table_name = models.CharField(db_column='TableName', max_length=255, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'TableLookup'

    def __str__(self) -> str:
        """
        This function returns a TableLookup in a neat string format.
        """
        return f"{self.table_name}"


class TrainingDataset(models.Model):
    training_dataset_id = models.AutoField(db_column='TrainingDatasetID', primary_key=True)  
    claim_id = models.ForeignKey(Claim, models.PROTECT, db_column='ClaimID', blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'TrainingDataset'

    def __str__(self) -> str:
        """
        This function returns a TrainingDataset in a neat string format.
        """
        return f"{self.claim_id}"


class UploadedRecord(models.Model):
    uploaded_record_id = models.AutoField(db_column='UploadedRecordID', primary_key=True)  
    user_id = models.ForeignKey(UserProfile, models.PROTECT, db_column='UserID', blank=True, null=True)  
    claim_id = models.ForeignKey(Claim, models.PROTECT, db_column='ClaimID', blank=True, null=True)  
    feedback_id = models.ForeignKey(Feedback, models.PROTECT, db_column='FeedbackID', blank=True, null=True)  
    model_id = models.ForeignKey(PredictionModel, models.PROTECT, db_column='ModelID', blank=True, null=True)  
    predicted_settlement = models.FloatField(db_column='PredictedSettlement', blank=True, null=True)  
    upload_date = models.DateField(db_column='UploadDate', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'UploadedRecord'

    def __str__(self) -> str:
        """
        This function returns an UploadedRecord in a neat string format.
        """
        return f"{self.user_id} | {self.claim_id} | {self.feedback_id} | {self.model_id} | {self.predicted_settlement} | {self.upload_date}"


    @staticmethod
    def upload_claims_from_file(file, user: UserProfile, ignore_validation: bool) -> SimpleResultWithPayload:
        result = SimpleResultWithPayload()
        
        csv = pd.read_csv(file)
        
        claimValidationResult = SimpleResult()
        if not ignore_validation:
            claimValidationResult = Claim.validate_columns(csv)
            
        if not claimValidationResult.success:
            result.add_messages_from_result_and_mark_unsuccessful_if_error_found(claimValidationResult)
            return result
            
        claims: list[Claim] = Claim.create_claims_from_dataframe(csv)
        uploadedRecords = []
        
        try:
            with transaction.atomic():
                index = 0
                for claim in claims:
                    index += 1
                    try:
                        claim.save()
                    except ValueError as error:
                        result.add_error_message_and_mark_unsuccessful(f"Row {index} | {error.__str__()}")
                        continue
                    
                    uploadedRecord = UploadedRecord()
                    uploadedRecord.user_id = None if not user else user # TODO: remove this check when account creation is implemented
                    uploadedRecord.claim_id = claim
                    uploadedRecord.feedback_id = None
                    uploadedRecord.model_id = None
                    uploadedRecord.predicted_settlement = None
                    uploadedRecord.upload_date = date.today()
                    
                    uploadedRecord.save()
                    uploadedRecords.append(uploadedRecord)
                
                if not result.success:
                    #raise an error so that django rolls back the transaction
                    raise AssertionError("Result was not successful")
                
        except AssertionError:
            return result
        
        result.payload = uploadedRecords
        
        return result
     
    @staticmethod
    def get_records_by_user(user: UserProfile) -> SimpleResultWithPayload:
        result = SimpleResultWithPayload()
        
        if user:
            result.payload = UploadedRecord.objects.filter(user_id = user.user_profile_id)
        else:
            result.add_info_message("User was null, returning records without a user")
            result.payload = UploadedRecord.objects.filter(user_id = None)
            
        return result
      

class PreprocessingStep(models.Model):
    preprocessing_step_id = models.AutoField(db_column='PreprocessingStepID', primary_key=True)
    preprocess_name = models.CharField(db_column='PreprocessName', max_length=255, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'PreprocessingStep'
    
    def __str__(self) -> str:
        """
        This function returns an PreprocessingStep in a neat string format.
        """
        return f"{self.preprocess_name}"


class PreprocessingModelMap(models.Model):
    preprocessing_model_map_id = models.AutoField(db_column='PreprocessingModelMapID', primary_key=True)
    preprocessing_step_id = models.ForeignKey(PreprocessingStep, models.PROTECT, db_column='PreprocessingStepID', blank=True, null=True)
    model_id = models.ForeignKey(PredictionModel, models.PROTECT, db_column='ModelID', blank=True, null=True)
    
    def __str__(self) -> str:
        """
        This function returns an PreprocessingStep in a neat string format.
        """
        return f"{self.preprocessing_step_id} | {self.model_id}"
    
    class Meta:
        managed = True
        db_table = 'PreprocessingModelMap'
