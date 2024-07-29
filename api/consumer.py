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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
enc_pkl = os.path.join(BASE_DIR,"media","encodings.pkl")
if os.path.exists(enc_pkl):
    with open(enc_pkl, "rb") as f:
        data = pickle.load(f)
else:
    data = {"names": [], "encodings": []}
    with open(enc_pkl, "wb") as f:
        pickle.dump(data, f)
names = data["names"]
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
                else:
                    top, right, bottom, left = face_location
                    cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(self.frame, "Unknown", (left + 6, top - 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), 1)
            self.buffer_img = await self.loop.run_in_executor(None, cv2.imencode, '.jpeg', self.frame)
            self.b64_img = base64.b64encode(self.buffer_img[1]).decode('utf-8')
            asyncio.sleep(100/1000)
            await self.send(self.b64_img)