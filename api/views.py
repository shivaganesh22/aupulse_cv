from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import cv2
import pickle
import os
import numpy as np
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
facedetect = cv2.CascadeClassifier('media/haarcascade_frontalface_default.xml')
class CreateStudentView1(APIView):
    def capture_and_store_face(self, name, image_path):
        faces_data = None  # Initialize with None to check if face is captured
        file_data = image_path.read()
        np_array = np.frombuffer(file_data, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            x, y, w, h = faces[0]  # Take the first detected face
            crop_img = frame[y:y+h, x:x+w, :]
            resized_img = cv2.resize(crop_img, (50, 50))
            faces_data = resized_img  # Save the detected face
            cv2.putText(frame, "Face Captured", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
        cv2.imshow("Frame", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        if faces_data is not None:
            faces_data = faces_data.reshape(1, -1)  # Reshape to (1, 7500)

            if 'names.pkl' not in os.listdir('media/'):
                names = [name]
                with open('media/names.pkl', 'wb') as f:
                    pickle.dump(names, f)
            else:
                with open('media/names.pkl', 'rb') as f:
                    names = pickle.load(f)
                names.append(name)
                with open('media/names.pkl', 'wb') as f:
                    pickle.dump(names, f)

            if 'faces_data.pkl' not in os.listdir('media/'):
                with open('media/faces_data.pkl', 'wb') as f:
                    pickle.dump(faces_data, f)
            else:
                with open('media/faces_data.pkl', 'rb') as f:
                    faces = pickle.load(f)
                faces = np.append(faces, faces_data, axis=0)
                with open('media/faces_data.pkl', 'wb') as f:
                    pickle.dump(faces, f)
    def post(self, request):
        image_path = request.FILES.get('profile')
        name = request.data.get('hall_ticket')

        if image_path and name:
            self.capture_and_store_face(name, image_path)
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
from sklearn.neighbors import KNeighborsClassifier
class ReadfacesView():
    video=cv2.VideoCapture(0)
    with open('media/names.pkl', 'rb') as w:
            LABELS=pickle.load(w)
    with open('media/faces_data.pkl', 'rb') as f:
        FACES=pickle.load(f)
    def read(self):
        print('Shape of Faces matrix --> ', self.FACES.shape)

        knn=KNeighborsClassifier(n_neighbors=1)
        knn.fit(self.FACES, self.LABELS)

        while True:
            ret,frame=self.video.read()
            gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces=facedetect.detectMultiScale(gray, 1.3 ,5)
            for (x,y,w,h) in faces:
                crop_img=frame[y:y+h, x:x+w, :]
                resized_img=cv2.resize(crop_img, (50,50)).flatten().reshape(1,-1)
                output=knn.predict(resized_img)
                # ts=time.time()
                # date=datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
                # timestamp=datetime.fromtimestamp(ts).strftime("%H:%M-%S")
                # exist=os.path.isfile("Attendance/Attendance_" + date + ".csv")
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 1)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(50,50,255),2)
                cv2.rectangle(frame,(x,y-40),(x+w,y),(50,50,255),-1)
                cv2.putText(frame, str(output[0]), (x,y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                cv2.rectangle(frame, (x,y), (x+w, y+h), (50,50,255), 1)
                # attendance=[str(output[0]), str(timestamp)]
            # imgBackground[162:162 + 480, 55:55 + 640] = frame
            cv2.imshow("Frame",frame)
            k=cv2.waitKey(1)

            if k==ord('q'):
                break
        self.video.release()
        cv2.destroyAllWindows()
ReadfacesView().read()
