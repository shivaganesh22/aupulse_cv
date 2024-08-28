import numpy as np
import cv2
from django.shortcuts import render
import os
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import asyncio
import pickle
import face_recognition
from datetime import datetime
import csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
enc_pkl = os.path.join(BASE_DIR,"media","encodings.pkl")
if os.path.exists(enc_pkl):
    with open(enc_pkl, "rb") as f:
        data = pickle.load(f)
else:
    data = {"hall_tickets": [], "encodings": []}
    with open(enc_pkl, "wb") as f:
        pickle.dump(data, f)
names = data["hall_tickets"]
encodings = data["encodings"]
class VideoStreamConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.loop = asyncio.get_running_loop()
        await self.accept()

    async def disconnect(self, close_code):
        self.stop = True
        raise StopConsumer()
            
    async def receive(self, bytes_data):  
        if not (bytes_data):
            print('Closed connection')
            await self.close()
        else:
            self.frame = await self.loop.run_in_executor(None, cv2.imdecode, np.frombuffer(bytes_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            face_locations = face_recognition.face_locations(self.frame)
            face_encodings = face_recognition.face_encodings(self.frame, face_locations)
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(encodings, face_encoding)
                face_distance = face_recognition.face_distance(encodings, face_encoding)
                best_match_index = np.argmin(face_distance)

                if matches[best_match_index]:
                    name = names[best_match_index]
                    top, right, bottom, left = face_location
                    cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(self.frame, name, (left + 6, top - 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    capture_log_csv = os.path.join(BASE_DIR, "media", f"attendance_{current_date}.csv")

                    # Check for duplicates
                    already_added = False
                    if os.path.exists(capture_log_csv):
                        with open(capture_log_csv, "r") as csvfile:
                            reader = csv.DictReader(csvfile)
                            for row in reader:
                                if row["hall_ticket"] == name:
                                    already_added = True
                                    break

                    # Append the hall_ticket and timestamp only if not already added
                    if not already_added:
                        with open(capture_log_csv, "a", newline="") as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=["hall_ticket", "timestamp"])
                            if os.path.getsize(capture_log_csv) == 0:
                                writer.writeheader()  # Write header if file is empty
                            writer.writerow({"hall_ticket": name, "timestamp": timestamp})
                else:
                    top, right, bottom, left = face_location
                    cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(self.frame, "Unknown", (left + 6, top - 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
            self.buffer_img = await self.loop.run_in_executor(None, cv2.imencode, '.jpeg', self.frame)
            self.b64_img = base64.b64encode(self.buffer_img[1]).decode('utf-8')
            asyncio.sleep(100/1000)
            await self.send(self.b64_img)

# import json
# import numpy as np
# import cv2
# from django.shortcuts import render
# import os
# import base64
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.exceptions import StopConsumer
# import asyncio
# import pickle
# import face_recognition
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# enc_pkl = os.path.join(BASE_DIR,"media","encodings.pkl")
# if os.path.exists(enc_pkl):
#     with open(enc_pkl, "rb") as f:
#         data = pickle.load(f)
# else:
#     data = {"hall_tickets": [], "encodings": []}
#     with open(enc_pkl, "wb") as f:
#         pickle.dump(data, f)
# names = data["hall_tickets"]
# encodings = data["encodings"]

# class VideoStreamConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.loop = asyncio.get_running_loop()
#         await self.accept()
#         self.stop = False
#         self.cap = None

#     async def disconnect(self, close_code):
#         self.stop = True
#         if self.cap:
#             self.cap.release()
#         raise StopConsumer()

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         if data['action'] == 'start_stream':
#             await self.start_stream(data['rtsp_url'])
#         elif data['action'] == 'stop_stream':
#             await self.stop_stream()

#     async def start_stream(self, rtsp_url):
#         self.stop = False
#         self.cap = cv2.VideoCapture(rtsp_url)
#         asyncio.create_task(self.process_rtsp_stream())

#     async def stop_stream(self):
#         self.stop = True
#         if self.cap:
#             self.cap.release()
#             self.cap = None

#     async def process_rtsp_stream(self):
#         while not self.stop:
#             ret, self.frame = await self.loop.run_in_executor(None, self.cap.read)
#             if not ret:
#                 print("Failed to receive frame from RTSP stream")
#                 await asyncio.sleep(1)
#                 continue

#             # face_locations = await self.loop.run_in_executor(None, face_recognition.face_locations, self.frame)
#             # face_encodings = await self.loop.run_in_executor(None, face_recognition.face_encodings, self.frame, face_locations)

#             # for face_encoding, face_location in zip(face_encodings, face_locations):
#             #     matches = face_recognition.compare_faces(encodings, face_encoding)
#             #     face_distance = face_recognition.face_distance(encodings, face_encoding)
#             #     best_match_index = np.argmin(face_distance)

#             #     if matches[best_match_index]:
#             #         name = names[best_match_index]
#             #         top, right, bottom, left = face_location
#             #         cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 255, 0), 2)
#             #         cv2.putText(self.frame, name, (left + 6, top - 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
#             #     else:
#             #         top, right, bottom, left = face_location
#             #         cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
#             #         cv2.putText(self.frame, "Unknown", (left + 6, top - 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)

#             self.buffer_img = await self.loop.run_in_executor(None, cv2.imencode, '.jpeg', self.frame)
#             self.b64_img = base64.b64encode(self.buffer_img[1]).decode('utf-8')
#             await self.send(self.b64_img)
#             # await asyncio.sleep(0.033)  # Adjust for desired frame rate