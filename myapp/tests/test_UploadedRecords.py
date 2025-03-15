from django.test import TestCase

from myapp.models import UploadedRecord, UserProfile
from myapp.utility.SimpleResults import SimpleResultWithPayload

import pandas as pd

"""
TODO
set up:
    see baseview test
    run TestModels.SetUp to get models into the db

test get_records_by_user
test upload_claims_from_file
"""

class TestUploadedRecords(TestCase):
    
    def test_record_upload_from_file(self):
        
        # pandas is weird about reading from the same file twice so we have to open it twice
        with open('myapp/tests/data/TestClaimData.csv') as f:
            df = pd.read_csv(f)
        settlement_value = df['SettlementValue'][0]
            
        with open('myapp/tests/data/TestClaimData.csv') as f:
            result = UploadedRecord.upload_claims_from_file(f, None)
            
        self.assertNotEqual(result, None)
        self.assertTrue(result.success, "Data upload was unsuccessful")      
        self.assertEqual(result.payload[0].claim_id.settlement_value, settlement_value)
        
    def test_failed_record_upload_from_file(self):
                    
        with open('myapp/tests/data/InvalidTestClaimData.csv') as f:
            result = UploadedRecord.upload_claims_from_file(f, None)
            
        self.assertNotEqual(result, None)
        self.assertFalse(result.success, "Data upload was not marked as failed")
        self.assertEqual(result.payload, None)
        
    def test_get_records_by_user(self):
        
        # create a dummy user
        user = UserProfile()
        user.save()
        
        # create a dummy record
        record = UploadedRecord()
        record.user_id = user
        record.save()
        
        result: SimpleResultWithPayload = UploadedRecord.get_records_by_user(user)
        
        self.assertNotEqual(result, None)
        self.assertTrue(result.success, "Data read was unsuccessful")
        
        self.assertEqual(len(result.payload), 1)
        self.assertEqual(result.payload[0].uploaded_record_id, record.uploaded_record_id)
        
    def test_get_records_no_user(self):
        
        # create a dummy record
        record = UploadedRecord()
        record.user_id = None
        record.save()
        
        result: SimpleResultWithPayload = UploadedRecord.get_records_by_user(None)
        
        self.assertNotEqual(result, None)
        self.assertTrue(result.success, "Data read was unsuccessful")
        
        self.assertEqual(len(result.payload), 1)
        self.assertEqual(result.payload[0].uploaded_record_id, record.uploaded_record_id)
