# qr_scanner/models.py
from django.db import models

class BusEntry(models.Model):
    bus_number = models.CharField(max_length=50)
    entry_time = models.DateTimeField(auto_now_add=True)
    #driver_name = models.CharField(max_length=255)
    #driver_number = models.CharField(max_length=20)
    
