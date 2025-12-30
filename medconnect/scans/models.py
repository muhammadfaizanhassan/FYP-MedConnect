from django.db import models

class Scan(models.Model):
    image = models.ImageField(upload_to='scans/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

