import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
from django.apps import apps  # Import apps for dynamic model loading
import threading

scanned_data = []  # List to store scanned QR code details
lock = threading.Lock()  # Thread-safe lock for data manipulation

def scan_qr_code_stream():
    """Continuously scan QR codes using the camera."""
    global scanned_data
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)
        with lock:  # Ensure thread-safe access to scanned_data
            for obj in decoded_objects:
                bus_number = obj.data.decode('utf-8')
                if not any(entry['bus_number'] == bus_number for entry in scanned_data):
                    try:
                        # Dynamically fetch models
                        BusEntry = apps.get_model('qr_scanner', 'BusEntry')
                        DriverInfo = apps.get_model('qr_generator', 'DriverInfo')

                        driver_info = DriverInfo.objects.get(bus_number=bus_number)
                        entry = {
                            'bus_number': bus_number,
                            'driver_name': driver_info.driver_name,
                            'driver_number': driver_info.driver_number,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        scanned_data.append(entry)
                        BusEntry.objects.create(
                            bus_number=bus_number,
                            driver_name=driver_info.driver_name,
                            driver_number=driver_info.driver_number,
                        )
                    except DriverInfo.DoesNotExist:
                        print(f"Bus number {bus_number} not found in database!")

        # Display the video feed
        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()
