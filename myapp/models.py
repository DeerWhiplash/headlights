# This is an auto-generated Django model module.

# Remember to migrate to the database using the following:
#   manage.py makemigrations <app_name>
#   manage.py migrate <app_name>

# If this doesn't work you may need to reset your migrations
#   delete all files in the migrations folder except __init__.py
#   run python manage.py migrate --fake <app_name> zero

# Changes made to the database can turned into models using the following:
#   python manage.py inspectdb > models.py

from django.db import models


class Bod(models.Model):
    bodid = models.AutoField(db_column='BodID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=255, blank=True, null=True)  # Field name made lowercase.
    permissionid = models.ForeignKey('Permissionlevel', models.PROTECT, db_column='PermissionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'Bod'


class Claim(models.Model):
    claimid = models.AutoField(db_column='ClaimID', primary_key=True)  # Field name made lowercase.
    settlementvalue = models.FloatField(db_column='SettlementValue', blank=True, null=True)  # Field name made lowercase.
    accidenttype = models.CharField(db_column='AccidentType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    injuryprognosis = models.IntegerField(db_column='InjuryPrognosis', blank=True, null=True)  # Field name made lowercase.
    specialhealthexpenses = models.FloatField(db_column='SpecialHealthExpenses', blank=True, null=True)  # Field name made lowercase.
    specialreduction = models.FloatField(db_column='SpecialReduction', blank=True, null=True)  # Field name made lowercase.
    specialoverage = models.FloatField(db_column='SpecialOverage', blank=True, null=True)  # Field name made lowercase.
    generalrest = models.FloatField(db_column='GeneralRest', blank=True, null=True)  # Field name made lowercase.
    specialadditionalinjury = models.FloatField(db_column='SpecialAdditionalInjury', blank=True, null=True)  # Field name made lowercase.
    specialearningsloss = models.FloatField(db_column='SpecialEarningsLoss', blank=True, null=True)  # Field name made lowercase.
    specialusageloss = models.FloatField(db_column='SpecialUsageLoss', blank=True, null=True)  # Field name made lowercase.
    specialmedications = models.FloatField(db_column='SpecialMedications', blank=True, null=True)  # Field name made lowercase.
    specialassetdamage = models.FloatField(db_column='SpecialAssetDamage', blank=True, null=True)  # Field name made lowercase.
    specialrehabilitation = models.FloatField(db_column='SpecialRehabilitation', blank=True, null=True)  # Field name made lowercase.
    specialfixes = models.FloatField(db_column='SpecialFixes', blank=True, null=True)  # Field name made lowercase.
    generalfixed = models.FloatField(db_column='GeneralFixed', blank=True, null=True)  # Field name made lowercase.
    generaluplift = models.FloatField(db_column='GeneralUplift', blank=True, null=True)  # Field name made lowercase.
    specialloanervehicle = models.FloatField(db_column='SpecialLoanerVehicle', blank=True, null=True)  # Field name made lowercase.
    specialtripcosts = models.FloatField(db_column='SpecialTripCosts', blank=True, null=True)  # Field name made lowercase.
    specialjourneyexpenses = models.FloatField(db_column='SpecialJourneyExpenses', blank=True, null=True)  # Field name made lowercase.
    specialtherapy = models.FloatField(db_column='SpecialTherapy', blank=True, null=True)  # Field name made lowercase.
    exceptionalcircumstances = models.IntegerField(db_column='ExceptionalCircumstances', blank=True, null=True)  # Field name made lowercase.
    minorpsychologicalinjury = models.IntegerField(db_column='MinorPsychologicalInjury', blank=True, null=True)  # Field name made lowercase.
    dominantinjury = models.CharField(db_column='DominantInjury', max_length=255, blank=True, null=True)  # Field name made lowercase.
    whiplash = models.IntegerField(db_column='Whiplash', blank=True, null=True)  # Field name made lowercase.
    vehicletype = models.CharField(db_column='VehicleType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    weatherconditions = models.CharField(db_column='WeatherConditions', max_length=255, blank=True, null=True)  # Field name made lowercase.
    accidentdate = models.IntegerField(db_column='AccidentDate', blank=True, null=True)  # Field name made lowercase.
    claimdate = models.IntegerField(db_column='ClaimDate', blank=True, null=True)  # Field name made lowercase.
    vehicleage = models.IntegerField(db_column='VehicleAge', blank=True, null=True)  # Field name made lowercase.
    driverage = models.IntegerField(db_column='DriverAge', blank=True, null=True)  # Field name made lowercase.
    numberofpassengers = models.IntegerField(db_column='NumberOfPassengers', blank=True, null=True)  # Field name made lowercase.
    accidentdescription = models.CharField(db_column='AccidentDescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    injurydescription = models.CharField(db_column='InjuryDescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    policereportfiled = models.IntegerField(db_column='PoliceReportFiled', blank=True, null=True)  # Field name made lowercase.
    witnesspresent = models.IntegerField(db_column='WitnessPresent', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'Claim'


class Feedback(models.Model):
    feedbackid = models.AutoField(db_column='FeedbackID', primary_key=True)  # Field name made lowercase.
    bodid = models.ForeignKey(Bod, models.PROTECT, db_column='BodID', blank=True, null=True)  # Field name made lowercase.
    rating = models.IntegerField(db_column='Rating', blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'Feedback'


class Log(models.Model):
    logid = models.AutoField(db_column='LogID', primary_key=True)  # Field name made lowercase.
    logtime = models.DateTimeField(db_column='LogTime', blank=True, null=True)  # Field name made lowercase.
    bodid = models.ForeignKey(Bod, models.PROTECT, db_column='BodID', blank=True, null=True)  # Field name made lowercase.
    affectedtableid = models.ForeignKey('Tablelookup', models.PROTECT, db_column='AffectedTableID', blank=True, null=True)  # Field name made lowercase.
    operationperformed = models.ForeignKey('Operationlookup', models.PROTECT, db_column='OperationPerformed', blank=True, null=True)  # Field name made lowercase.
    successful = models.BooleanField(db_column='Successful', blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'Log'


class Model(models.Model):
    modelid = models.AutoField(db_column='ModelID', primary_key=True)  # Field name made lowercase.
    modelname = models.CharField(db_column='ModelName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  # Field name made lowercase.
    filepath = models.CharField(db_column='FilePath', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'Model'


class Operationlookup(models.Model):
    operationid = models.AutoField(db_column='OperationID', primary_key=True)  # Field name made lowercase.
    operationname = models.CharField(db_column='OperationName', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'OperationLookup'


class Permissionlevel(models.Model):
    permissionid = models.AutoField(db_column='PermissionID', primary_key=True)  # Field name made lowercase.
    systempermissionlevel = models.IntegerField(db_column='SystemPermissionLevel', blank=True, null=True)  # Field name made lowercase.
    mlpermissionlevel = models.IntegerField(db_column='MLPermissionLevel', blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'PermissionLevel'


class Tablelookup(models.Model):
    tableid = models.AutoField(db_column='TableID', primary_key=True)  # Field name made lowercase.
    tablename = models.CharField(db_column='TableName', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'TableLookup'


class Trainingdataset(models.Model):
    trainingdatasetid = models.AutoField(db_column='TrainingDatasetID', primary_key=True)  # Field name made lowercase.
    claimid = models.ForeignKey(Claim, models.PROTECT, db_column='ClaimID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'TrainingDataset'


class Uploadedrecord(models.Model):
    uploadedrecordid = models.AutoField(db_column='UploadedRecordID', primary_key=True)  # Field name made lowercase.
    bodid = models.ForeignKey(Bod, models.PROTECT, db_column='BodID', blank=True, null=True)  # Field name made lowercase.
    claimid = models.ForeignKey(Claim, models.PROTECT, db_column='ClaimID', blank=True, null=True)  # Field name made lowercase.
    feedbackid = models.ForeignKey(Feedback, models.PROTECT, db_column='FeedbackID', blank=True, null=True)  # Field name made lowercase.
    modelid = models.ForeignKey(Model, models.PROTECT, db_column='ModelID', blank=True, null=True)  # Field name made lowercase.
    predictedsettlement = models.FloatField(db_column='PredictedSettlement', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'UploadedRecord'
