from django.db import models

class Conversation(models.Model):
    prompt = models.CharField(max_length=500)
    response = models.TextField()
