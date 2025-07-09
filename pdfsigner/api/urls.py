from django.urls import path
from . import views

urlpatterns = [
    path('sign/', views.sign_pdf, name='sign_pdf'),
    path('verify/', views.verify_pdf, name='verify_pdf'),
]
