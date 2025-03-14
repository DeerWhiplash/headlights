from django.db import models

class Model(models.Model):
    model_id = models.AutoField(db_column='ModelID', primary_key=True)  
    model_name = models.CharField(db_column='ModelName', max_length=255, blank=True, null=True)  
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  
    filepath = models.CharField(db_column='FilePath', max_length=255, blank=True, null=True)  
    price_per_prediction = models.FloatField(db_column='PricePerPrediction', blank=True, null=True)

    class Meta:
        managed = False  # ensures Django doesn't try to create or modify the table
        db_table = 'Model'

    def __str__(self) -> str:
        """
        This function returns a Model in a neat string format.
        """
        return f"{self.model_name} | {self.notes} | {self.filepath} | {self.price_per_prediction}"
