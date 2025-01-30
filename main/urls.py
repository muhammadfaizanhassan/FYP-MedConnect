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
    

    # Scans feature (upload analysis, etc.)
    path('doctor/dashboard/upload/', include('scans.urls', namespace='scans')),  # ensure scans has app_name in its urls.py

    # Payment flow
    
    path("payment/<int:appointment_id>/", views.payment, name="payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-failure/", views.payment_failure, name="payment_failure"),
    
    
    #review
    path("review/<int:appointment_id>/", views.add_review, name="add_review"),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
]
