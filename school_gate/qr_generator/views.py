# qr_generator/views.py
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
from .models import DriverInfo
import csv
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile 
from django.conf import settings

def download_sample_csv(request):
    # Generate and download sample CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample.csv"'
    writer = csv.writer(response)
    writer.writerow(['DriverName', 'BusNumber', 'DriverNumber'])
    writer.writerow(['John Doe', 'Bus1234', '1234567890'])
    return response

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        # Clear previous QR codes (optional, based on your preference)
        DriverInfo.objects.all().delete()
        qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        if os.path.exists(qr_codes_dir):
            for file in os.listdir(qr_codes_dir):
                os.remove(os.path.join(qr_codes_dir, file))

        # Generate QR codes
        for row in reader:
            driver_name = row['DriverName']
            bus_number = row['BusNumber']
            driver_number = row['DriverNumber']

            # Generate QR code
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
            qr.add_data(bus_number)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.convert("RGB")

            # Add bus number text below QR code
            draw = ImageDraw.Draw(qr_img)
            font = ImageFont.load_default()
            text_bbox = draw.textbbox((0, 0), bus_number, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            img_width, img_height = qr_img.size
            text_x = (img_width - text_width) // 2
            text_y = img_height - text_height
            draw.text((text_x, text_y), bus_number, font=font, fill="black")

            # Save QR code
            img_path = os.path.join(qr_codes_dir, f'{bus_number}.png')
            qr_img.save(img_path)

            # Save to database
            DriverInfo.objects.create(
                driver_name=driver_name,
                bus_number=bus_number,
                driver_number=driver_number,
                qr_code_image=img_path,
            )

        # Create a ZIP file of QR codes
        zip_file_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(qr_codes_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, qr_codes_dir)
                    zipf.write(file_path, arcname)

        # Render the template with the success message and ZIP file path
        return render(request, 'qr_generator/upload_csv.html', {
            'success': True,
            'zip_url': f'/media/qr_codes.zip'
        })

    return render(request, 'qr_generator/upload_csv.html')

def download_qr_codes(request):
    # Path to the directory where QR codes are stored
    qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')

    # Create a ZIP file in memory
    zip_file_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        # Add each QR code image to the ZIP file
        for root, dirs, files in os.walk(qr_codes_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, qr_codes_dir)  # Preserve relative path in ZIP
                zipf.write(file_path, arcname)

    # Serve the ZIP file as a response
    with open(zip_file_path, 'rb') as zipf:
        response = HttpResponse(zipf.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'

    # Delete the ZIP file after serving it
    os.remove(zip_file_path)
    return response

