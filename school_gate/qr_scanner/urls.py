'''from django.urls import path
from . import views

urlpatterns = [
    path('video-feed/', views.video_feed, name='video_feed'),
    path('live-feed/', views.live_feed, name='live_feed'),
    path('get-scanned-data/', views.get_scanned_data, name='get_scanned_data'),
]
'''
from django.urls import path
from . import views

app_name = "qr_scanner"

urlpatterns = [
    path('live-feed/', views.live_feed, name='live_feed'),
    path('video-feed/', views.video_feed, name='video_feed'),
    path('get-scanned-data/', views.get_scanned_data, name='get_scanned_data'),  # New endpoint
]

