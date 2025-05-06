from django.test import TestCase
from myapp.models import Claim, TrainingDataset

class TestTrainingDataset(TestCase):
    def test_claim_creation_from_dataframe(self):
        #create dummy claim
        claim = Claim()
        claim.save()
        
        #insert into TrainingDataset
        result = TrainingDataset.add_claims_to_training_data([claim])
        
        self.assertTrue(result.success, "TrainingDataset insertion failed")
        
        created_training_data: TrainingDataset = result.payload[0]
        
        self.assertEqual(created_training_data.claim_id.claim_id, claim.claim_id)
