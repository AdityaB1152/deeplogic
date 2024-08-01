from django.db import models

class Invoice(models.Model):
    pdf = models.FileField(upload_to='invoices/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)
    image_path = models.CharField(max_length=255, blank=True)
    hash = models.CharField(max_length=64)
