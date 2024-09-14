from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import DoctorRegistrationForm, PatientRegistrationForm, AppointmentForm
from .models import Appointment
from django.db.models import Q
from django.contrib.auth.models import User
from .models import DoctorProfile, PatientProfile


# Home view with role-based checks
def home(request):
    from .models import DoctorProfile, PatientProfile  # Local import to avoid circular import
    is_doctor = False
    is_patient = False

    # Check if the logged-in user is a doctor or patient
    if request.user.is_authenticated:
        if DoctorProfile.objects.filter(user=request.user).exists():
            is_doctor = True
        elif PatientProfile.objects.filter(user=request.user).exists():
            is_patient = True

    return render(request, 'home.html', {'is_doctor': is_doctor, 'is_patient': is_patient})


# Static pages
def about(request):
    return render(request, 'about.html')


def chatbot(request):
    return render(request, 'chatbot.html')


def appointment(request):
    return render(request, 'appointment.html')


def doctor(request):
    return render(request, 'doctor.html')


def contact(request):
    return render(request, 'contact.html')


def privacy(request):
    return render(request, 'privacy.html')


def terms(request):
    return render(request, 'terms.html')


# Registration views
def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            DoctorProfile.objects.create(
                user=user,
                specialization=form.cleaned_data['specialization']
            )
            messages.success(request, "Doctor registered successfully!")
            return redirect('login')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'register_doctor.html', {'form': form})

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            PatientProfile.objects.create(
                user=user,
                age=form.cleaned_data['age'],
                medical_history=form.cleaned_data['medical_history']
            )
            messages.success(request, "Patient registered successfully!")
            return redirect('login')
    else:
        form = PatientRegistrationForm()
    return render(request, 'register_patient.html', {'form': form})


# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Check if the user is a Doctor or a Patient and redirect accordingly
            from .models import DoctorProfile, PatientProfile  # Local import
            if DoctorProfile.objects.filter(user=user).exists():
                return redirect('doctor_dashboard')  # Redirect to doctor dashboard
            elif PatientProfile.objects.filter(user=user).exists():
                return redirect('patient_dashboard')  # Redirect to patient dashboard
            else:
                return redirect('home')  # Default redirection if neither

        else:
            # Show an error message for invalid credentials
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


# Logout view
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# Doctor Dashboard View
@login_required
def doctor_dashboard(request):
    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('appointment_date', 'appointment_time')

        if request.method == 'POST':
            appointment_id = request.POST.get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id, doctor=doctor_profile)
            appointment.is_confirmed = True
            appointment.save()
            messages.success(request, "Appointment confirmed successfully.")

        return render(request, 'doctor_dashboard.html', {'appointments': appointments})

    except DoctorProfile.DoesNotExist:
        return redirect('home')



# Patient Dashboard View
@login_required
def patient_dashboard(request):
    # Check if the logged-in user is a patient
    if PatientProfile.objects.filter(user=request.user).exists():
        # Get all appointments for the logged-in patient
        appointments = Appointment.objects.filter(patient=request.user).order_by('appointment_date', 'appointment_time')

        # Render the template and pass the appointments to it
        return render(request, 'patient_dashboard.html', {'appointments': appointments})
    else:
        return HttpResponseForbidden("You are not authorized to view this page.")


# Appointment Booking View
from django.shortcuts import redirect
from .models import Appointment, DoctorProfile

@login_required
def book_appointment(request):
    search_query = request.GET.get('search', '')

    # Search for doctors by name or specialization
    if search_query:
        doctors = DoctorProfile.objects.filter(user__username__icontains=search_query) | \
                  DoctorProfile.objects.filter(specialization__icontains=search_query)
    else:
        doctors = DoctorProfile.objects.all()

    if request.method == 'POST':
        selected_doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')

        try:
            selected_doctor = DoctorProfile.objects.get(id=selected_doctor_id)
            
            # Create the appointment as unconfirmed
            Appointment.objects.create(
                doctor=selected_doctor,
                patient=request.user,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                is_confirmed=False,  # Initially unconfirmed
            )

            messages.success(request, "Appointment booked! Waiting for doctor confirmation.")
            return redirect('patient_dashboard')

        except DoctorProfile.DoesNotExist:
            messages.error(request, "The selected doctor does not exist.")

    return render(request, 'book_appointment.html', {'doctors': doctors, 'search_query': search_query})

# Appointment Confirmation View
@login_required
def confirm_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == 'POST':
        appointment.is_confirmed = True
        appointment.save()
        messages.success(request, 'Appointment confirmed! Please proceed with payment.')
        return redirect('payment', appointment_id=appointment.id)

    return render(request, 'confirm_appointment.html', {'appointment': appointment})


# Payment View
@login_required
def payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user, is_confirmed=True)

    if request.method == 'POST':
        # Simulate payment using JazzCash or EasyPaisa
        payment_method = request.POST.get('payment_method')
        if payment_method:
            # Call the payment API (simulated for now)
            payment_success = process_payment(payment_method, appointment)

            if payment_success:
                appointment.payment_status = True
                appointment.save()
                messages.success(request, 'Payment successful!')
                return redirect('home')
            else:
                messages.error(request, 'Payment failed. Please try again.')

    return render(request, 'payment.html', {'appointment': appointment})


def process_payment(payment_method, appointment):
    # Simulate payment success (In real-world, this would call the API)
    if payment_method == 'jazzcash':
        # Simulate JazzCash payment (replace with API call)
        print(f"Processing JazzCash payment for appointment {appointment.id}")
    elif payment_method == 'easypaisa':
        # Simulate EasyPaisa payment (replace with API call)
        print(f"Processing EasyPaisa payment for appointment {appointment.id}")
    return True  # Assume payment success for now


# Payment Success and Failure Views
@login_required
def payment_success(request):
    messages.success(request, 'Your payment was successful!')
    return redirect('home')


@login_required
def payment_failure(request):
    messages.error(request, 'Your payment failed. Please try again.')
    return redirect('payment')

from .models import Contact

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the data in the database
        Contact.objects.create(name=name, email=email, message=message)

        # Show a success message
        messages.success(request, 'Your message has been submitted successfully!')

        return redirect('contact')  # Redirect back to the contact page

    return render(request, 'contact.html')