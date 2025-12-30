from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    # path('chat/', include('chat.urls', namespace='chat')),
     path('chatbot/', views.chatbot, name='chatbot'),

    path('appointment/', views.appointment, name='appointment'),  # Static appointment info
    path('book-appointment/', views.book_appointment, name='book_appointment'),  # Dynamic booking
    path('doctor/', views.doctor, name='doctor'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/dashboard/upload/', include('scans.urls', namespace='scans')),  # Ensure scans has app_name
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('confirm-appointment/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('payment/<int:appointment_id>/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
]
