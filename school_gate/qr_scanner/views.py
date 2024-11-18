import cv2
from pyzbar.pyzbar import decode
from django.http import StreamingHttpResponse
from django.shortcuts import render
#from datetime import datetime
from django.utils.timezone import now, timedelta
from django.http import JsonResponse

# Global variable to store scanned QR codes
scanned_data = []
# Add a global set to store already detected QR codes
detected_codes = set()

'''def generate_frames():
    cap = cv2.VideoCapture(0)  # Open the camera
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Decode QR codes in the frame
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                qr_text = obj.data.decode('utf-8')
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Only process new QR codes
                if qr_text not in detected_codes:
                    print(f"Detected QR Code: {qr_text}")  # Debugging
                    detected_codes.add(qr_text)  # Mark this code as processed
                    scanned_data.append({"text": qr_text, "time": current_time})

            # Encode frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()
'''
from .models import BusEntry

def generate_frames():
    cap = cv2.VideoCapture(0)  # Open the camera
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            # Decode QR codes in the frame
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                qr_text = obj.data.decode('utf-8')
                current_time = now()

                # Check if this QR code was scanned within the last minute
                time_threshold = current_time - timedelta(minutes=1)
                recent_entry = BusEntry.objects.filter(
                    bus_number=qr_text,
                    entry_time__gte=time_threshold
                ).exists()

                if not recent_entry:
                    # Create a new entry for the bus
                    BusEntry.objects.create(bus_number=qr_text, entry_time=current_time)
                    print(f"Detected QR Code: {qr_text}")  # Debugging

            # Encode frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()




def video_feed(request):
    """
    Serve the video feed to the browser.
    """
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


'''def live_feed(request):
    """
    Render the webpage with the live feed and scanned QR code data.
    """
    print(f"Scanned Data Sent to Template: {scanned_data}")  # Debug
    return render(request, "qr_scanner/live_feed.html", {"scanned_data": scanned_data})
'''

def live_feed(request):
    """
    Render the webpage with the live feed and scanned QR code data.
    """
    scanned_data = BusEntry.objects.order_by('-entry_time')[:10]  # Show the latest 10 entries
    return render(request, "qr_scanner/live_feed.html", {"scanned_data": scanned_data})


def get_scanned_data(request):
    """
    API endpoint to return scanned QR codes from the database.
    """
    scanned_qr_codes = BusEntry.objects.all().order_by('-entry_time')
    data = [
        {"bus_number": entry.bus_number, "entry_time": entry.entry_time.strftime('%Y-%m-%d %H:%M:%S')}
        for entry in scanned_qr_codes
    ]
    return JsonResponse({"scanned_data": data})
