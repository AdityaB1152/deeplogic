from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_invoice, name='upload_invoice'),
    path('result/<int:invoice_id>/', views.result, name='result'),
]
