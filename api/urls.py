from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *

urlpatterns = [
    path('',home),
    path('faces/',read_faces),
    path('capture/',take_attendance),
    path('attendance/',update_attendance),
    path('api/attendance/',attendance_submit)
]