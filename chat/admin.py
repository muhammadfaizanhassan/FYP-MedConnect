from django.contrib import admin
from .models import ChatSession, Conversation

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'created_at', 'updated_at', 'get_message_count']
    list_filter = ['created_at', 'updated_at', 'user']
    search_fields = ['title', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.conversations.count()
    get_message_count.short_description = 'Messages'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'prompt_preview', 'response_preview', 'created_at']
    list_filter = ['created_at', 'session']
    search_fields = ['prompt', 'response']
    readonly_fields = ['created_at']
    
    def prompt_preview(self, obj):
        return obj.prompt[:50] + "..." if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt'
    
    def response_preview(self, obj):
        return obj.response[:50] + "..." if len(obj.response) > 50 else obj.response
    response_preview.short_description = 'Response'

