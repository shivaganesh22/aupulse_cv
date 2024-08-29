from django.shortcuts import render,redirect
from django.contrib import messages
import cv2
import pickle
import os
import numpy as np
import face_recognition
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
enc_pkl = os.path.join(BASE_DIR,"media","encodings.pkl")
def home(r):
    return render(r,'home.html')
def read_faces( request):
    res = requests.get('https://aupulse-api.vercel.app/api/student/')
    students = res.json()
    for student in students:
        profile_image_url = student['profile']
        response = requests.get(profile_image_url)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if face_encodings:
            face_encoding = face_encodings[0]
            hall_ticket = student['hall_ticket']
            face_image = frame[face_locations[0][0]:face_locations[0][2], face_locations[0][3]:face_locations[0][1]]
            face_image = cv2.resize(face_image, (250, 250))
            if os.path.exists(enc_pkl):
                with open(enc_pkl, "rb") as f:
                    data = pickle.load(f)
            else:
                data = {"hall_tickets": [], "encodings": []}
            data["hall_tickets"].append(hall_ticket)
            data["encodings"].append(face_encoding)
            with open(enc_pkl, "wb") as f:
                pickle.dump(data, f)
    messages.success(request,'Faces updated successfully')
    return redirect('/')
def take_attendance(r):
    return render(r,'index2.html')
def update_attendance(request):
    return render(request,'attendance.html')
import json
import csv
import os
import datetime
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def attendance_submit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        section_id = data.get('section_id')
        semester_id = data.get('semester_id')
        date = datetime.date.today().strftime('%Y-%m-%d')
        
        # Define API URLs
        timetable_url = f"https://aupulse-api.vercel.app/api/timetabledisplay/?section={section_id}&subject_semester={semester_id}&date={date}"
        students_url = f"https://aupulse-api.vercel.app/api/student/?section={section_id}&status=True"

        # Fetch timetable
        timetable_response = requests.get(timetable_url)
        if timetable_response.status_code != 200:
            return JsonResponse({'status': 'failed', 'message': 'Failed to fetch timetable'}, status=500)
        timetable_data = timetable_response.json()

        # Fetch students
        students_response = requests.get(students_url)
        if students_response.status_code != 200:
            return JsonResponse({'status': 'failed', 'message': 'Failed to fetch students'}, status=500)
        students_data = students_response.json()

        # Read attendance from CSV
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_file_path = os.path.join(BASE_DIR, "media", f"attendance_{date}.csv")
        attendance = {}
        
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    hall_ticket = row.get('hall_ticket')
                    if hall_ticket:
                        attendance[hall_ticket] = True  # Assuming if hall_ticket exists, status is True
        # Prepare JSON payload for each period
        attendance_data = []
        for period in timetable_data:
            period_id = period.get('id')
            for student in students_data:
                student_id = student.get('id')
                student_no = student.get('hall_ticket')
                status = attendance.get(student_no, False)
                attendance_data.append({
                    'student': student_id,
                    'period': period_id,
                    'status': status,
                })
        # Send attendance data to API
        attendance_api_url = "https://aupulse-api.vercel.app/api/attendance/"
        response = requests.post(
            attendance_api_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(attendance_data)
        )
        if response.status_code == 201:
            return JsonResponse({'status': 'success'}, status=200)
        else:
            return JsonResponse({'status': 'failed', 'message': 'Failed to submit attendance'}, status=500)

    return JsonResponse({'status': 'failed'}, status=400)
