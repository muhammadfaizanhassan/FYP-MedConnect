from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat, name='chat'),
    path('stream/', views.chat_stream, name='chat_stream'),
    path('new-session/', views.new_session, name='new_session'),
    path('delete-session/<uuid:session_id>/', views.delete_session, name='delete_session'),
]
