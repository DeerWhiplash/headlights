from django.test import TestCase
from myapp.models import Claim
import pandas as pd

class TestClaims(TestCase):
    def test_column_validation(self):
        valid_df = pd.DataFrame(columns=['SettlementValue', 'AccidentType', 'InjuryPrognosis', 
                                   'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage', 
                                   'GeneralRest', 'SpecialAdditionalInjury', 'SpecialEarningsLoss',	
                                   'SpecialUsageLoss', 'SpecialMedications', 'SpecialAssetDamage',
                                   'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed',	
                                   'GeneralUplift', 'SpecialLoanerVehicle', 'SpecialTripCosts',	
                                   'SpecialJourneyExpenses', 'SpecialTherapy', 'ExceptionalCircumstances',
                                   'MinorPsychologicalInjury', 'DominantInjury', 'Whiplash',
                                   'VehicleType', 'WeatherConditions', 'AccidentDate',	
                                   'ClaimDate', 'VehicleAge', 'DriverAge',
                                   'NumberOfPassengers', 'AccidentDescription', 'InjuryDescription',	
                                   'PoliceReportFiled', 'WitnessPresent', 'Gender'
                                   ])
        
        df_missing_columns = pd.DataFrame(columns=['SettlementValue', 'AccidentType'])
        
        df_excess_columns = pd.DataFrame(columns=['SettlementValue', 'AccidentType', 'InjuryPrognosis', 
                                   'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage', 
                                   'GeneralRest', 'SpecialAdditionalInjury', 'SpecialEarningsLoss',	
                                   'SpecialUsageLoss', 'SpecialMedications', 'SpecialAssetDamage',
                                   'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed',	
                                   'GeneralUplift', 'SpecialLoanerVehicle', 'SpecialTripCosts',	
                                   'SpecialJourneyExpenses', 'SpecialTherapy', 'ExceptionalCircumstances',
                                   'MinorPsychologicalInjury', 'DominantInjury', 'Whiplash',
                                   'VehicleType', 'WeatherConditions', 'AccidentDate',	
                                   'ClaimDate', 'VehicleAge', 'DriverAge',
                                   'NumberOfPassengers', 'AccidentDescription', 'InjuryDescription',	
                                   'PoliceReportFiled', 'WitnessPresent', 'Gender', 'extra column'
                                   ])
        
        
        valid_result = Claim.validate_columns(valid_df)
        missing_column_result = Claim.validate_columns(df_missing_columns)
        excess_column_result = Claim.validate_columns(df_excess_columns)
        
        self.assertTrue(valid_result.success, "Valid columns incorrectly identified as invalid")
        self.assertFalse(missing_column_result.success, "Missing columns were not noticed")
        self.assertFalse(excess_column_result.success, "Excess column was not noticed")
        
    def test_claim_creation_from_series(self):
        #create dataframe with valid columns
        df = pd.DataFrame(columns=['SettlementValue', 'AccidentType', 'InjuryPrognosis', 
                                   'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage', 
                                   'GeneralRest', 'SpecialAdditionalInjury', 'SpecialEarningsLoss',	
                                   'SpecialUsageLoss', 'SpecialMedications', 'SpecialAssetDamage',
                                   'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed',	
                                   'GeneralUplift', 'SpecialLoanerVehicle', 'SpecialTripCosts',	
                                   'SpecialJourneyExpenses', 'SpecialTherapy', 'ExceptionalCircumstances',
                                   'MinorPsychologicalInjury', 'DominantInjury', 'Whiplash',
                                   'VehicleType', 'WeatherConditions', 'AccidentDate',	
                                   'ClaimDate', 'VehicleAge', 'DriverAge',
                                   'NumberOfPassengers', 'AccidentDescription', 'InjuryDescription',	
                                   'PoliceReportFiled', 'WitnessPresent', 'Gender'
                                   ])
        
        #insert a row of normal data into the dataframe
        df.loc[0] = [520, 'Rear end', 5, 0, 0, 0, 0, 0, 0, 0, 
                     0, 0, 0, 0, 520, 0, 0, 0, 0, 0, 
                     0, 1, 'Arms', 1, 'Motorcycle', 
                     'Rainy', 2023314, 2023163, 13, 33, 
                     4, 'Side collision at an intersection.',
                     'Whiplash and minor bruises.', 1, 1, 'Male'
                     ]
        
        claim = Claim()
        for index, series in df.iterrows():
            claim = Claim.create_claim_from_series(series)
            
        self.assertEqual(claim.settlement_value, 520)
        
    
    def test_claim_creation_from_dataframe(self):
        #create dataframe with valid columns
        df = pd.DataFrame(columns=['SettlementValue', 'AccidentType', 'InjuryPrognosis', 
                                   'SpecialHealthExpenses', 'SpecialReduction', 'SpecialOverage', 
                                   'GeneralRest', 'SpecialAdditionalInjury', 'SpecialEarningsLoss',	
                                   'SpecialUsageLoss', 'SpecialMedications', 'SpecialAssetDamage',
                                   'SpecialRehabilitation', 'SpecialFixes', 'GeneralFixed',	
                                   'GeneralUplift', 'SpecialLoanerVehicle', 'SpecialTripCosts',	
                                   'SpecialJourneyExpenses', 'SpecialTherapy', 'ExceptionalCircumstances',
                                   'MinorPsychologicalInjury', 'DominantInjury', 'Whiplash',
                                   'VehicleType', 'WeatherConditions', 'AccidentDate',	
                                   'ClaimDate', 'VehicleAge', 'DriverAge',
                                   'NumberOfPassengers', 'AccidentDescription', 'InjuryDescription',	
                                   'PoliceReportFiled', 'WitnessPresent', 'Gender'
                                   ])
        
        #insert a row of normal data into the dataframe
        df.loc[0] = [520, 'Rear end', 5, 0, 0, 0, 0, 0, 0, 0, 
                     0, 0, 0, 0, 520, 0, 0, 0, 0, 0, 
                     0, 1, 'Arms', 1, 'Motorcycle', 
                     'Rainy', 2023314, 2023163, 13, 33, 
                     4, 'Side collision at an intersection.',
                     'Whiplash and minor bruises.', 1, 1, 'Male'
                     ]
        
        #create claims
        claims: list[Claim] = Claim.create_claims_from_dataframe(df)
        
        #check if settlement value was correctly assigned
        self.assertEqual(claims[0].settlement_value, 520)
        
        