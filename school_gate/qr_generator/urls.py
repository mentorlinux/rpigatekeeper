from django.urls import path
from . import views

urlpatterns = [
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('download-sample/', views.download_sample_csv, name='download_sample_csv'),
    path('download-qr-codes/', views.download_qr_codes, name='download_qr_codes'),  # New URL
]
