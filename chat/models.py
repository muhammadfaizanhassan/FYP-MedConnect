from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from main.fields import EncryptedTextField
import uuid

class ChatSession(models.Model):
    """Represents a chat session (like ChatGPT conversations)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True, help_text="Auto-generated from first message")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
    
    def __str__(self):
        return self.title or f"Chat {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_message_count(self):
        return self.conversations.count()

class Conversation(models.Model):
    """Individual message exchange within a session"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='conversations')
    # Encrypted fields for HIPAA compliance - chat may contain PHI
    prompt = EncryptedTextField(help_text="Encrypted user prompt")
    response = EncryptedTextField(help_text="Encrypted AI response")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        return f"{self.session.title or 'Chat'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
