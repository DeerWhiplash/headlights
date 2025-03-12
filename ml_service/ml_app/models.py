"""
    share the database correctly - 
    the main app manages the schema, and the ML service 
    just reads and writes to the existing tables.
"""

from django.db import models

# ML models from original Django app
class Model(models.Model):
    model_id = models.AutoField(db_column='ModelID', primary_key=True)  
    model_name = models.CharField(db_column='ModelName', max_length=255, blank=True, null=True)  
    notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)  
    filepath = models.CharField(db_column='FilePath', max_length=255, blank=True, null=True)  
    price_per_prediction = models.FloatField(db_column='PricePerPrediction', blank=True, null=True)

    class Meta:
        managed = False  # Important: we're not managing this table, just using it
        db_table = 'Model'
