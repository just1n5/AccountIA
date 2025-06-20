from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('firebase-auth/', views.firebase_auth, name='firebase_auth'),
    path('health/', views.health_check, name='auth_health'),
]