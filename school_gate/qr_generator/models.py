from django.db import models

# qr_generator/models.py
class DriverInfo(models.Model):
    driver_name = models.CharField(max_length=255)
    bus_number = models.CharField(max_length=50)
    driver_number = models.CharField(max_length=20)
    qr_code_image = models.ImageField(upload_to='qr_codes/')
