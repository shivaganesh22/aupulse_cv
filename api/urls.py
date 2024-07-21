from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *

urlpatterns = [
    path('student/process/',CreateStudentView1.as_view()),
   
]