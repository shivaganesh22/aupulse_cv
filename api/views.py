from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import cv2
import pickle
import os
import numpy as np
import face_recognition
def home(r):
    return render(r,'index.html')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
enc_pkl = os.path.join(BASE_DIR,"media","encodings.pkl")
class CreateStudentView(APIView):
    def capture_and_store_face(self, name, image_path):
        faces_data = None  # Initialize with None to check if face is captured
        file_data = image_path.read()
        np_array = np.frombuffer(file_data, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if face_encodings:
            face_encoding = face_encodings[0]
            face_image = frame[face_locations[0][0]:face_locations[0][2], face_locations[0][3]:face_locations[0][1]]
            face_image = cv2.resize(face_image, (250, 250))
            if os.path.exists(enc_pkl):
                with open(enc_pkl, "rb") as f:
                    data = pickle.load(f)
            else:
                data = {"names": [], "encodings": []}
            # Add new face encoding
            data["names"].append(name)
            data["encodings"].append(face_encoding)
            with open(enc_pkl, "wb") as f:
                pickle.dump(data, f)
            print(f"Added new face: {name}")
        else:
            print("No face detected. Please try again.")
    def post(self, request):
        image_path = request.FILES.get('profile')
        name = request.data.get('hall_ticket')
        if image_path and name:
            self.capture_and_store_face(name, image_path)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


