from django.urls import path, include
from . import views

urlpatterns = [
    # Public-facing pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('register/patient/', views.register_patient, name='register_patient'),

    # Chat (includes URLs from a separate 'chat' app)
    path('chat/', include('chat.urls', namespace='chat')),

    # Appointment-related
    path('appointment/', views.appointment, name='appointment'),  # Possibly a static info page
    path('book-appointment/', views.book_appointment, name='book_appointment'),  # Dynamic booking

    # Dashboards
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),

    # Doctor confirms the appointment
    path('doctor/confirm/<int:appointment_id>/', views.doctor_confirm_appointment, name='doctor_confirm_appointment'),

    # Patient confirms the appointment (if your logic requires patient-side confirmation)
    path('patient/confirm/<int:appointment_id>/', views.patient_confirm_appointment, name='patient_confirm_appointment'),

    # Scans feature (upload analysis, etc.)
    path('scans/', include('scans.urls', namespace='scans')),

    # Payment flow
    path('payment/<int:appointment_id>/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
]
