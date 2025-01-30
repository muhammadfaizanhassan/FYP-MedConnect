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
from datetime import datetime, timedelta


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

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from together import Together

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        query = request.POST.get("query", "")

        # Initialize Together client with API key
        client = Together(api_key="5df0df3224f6530ce8bfded04afcb6e1c1fd61770039faf86034ea91d2d1308d")

        # Together API logic
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": query}],
            max_tokens=100,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            safety_model="meta-llama/Meta-Llama-Guard-3-8B",
        )

        # Extract response from Together
        chatbot_response = response.choices[0].message.content

        # Return JSON response
        return JsonResponse({"response": chatbot_response})

    return render(request, "chatbot.html")


# Registration views
def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create user first
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1']
                )
                
                # Create doctor profile
                DoctorProfile.objects.create(
                    user=user,
                    specialization=form.cleaned_data['specialization'],
                    office_location=form.cleaned_data['office_location'],
                    phone_number=form.cleaned_data.get('phone_number'),
                    consultation_fee=form.cleaned_data.get('consultation_fee'),
                    profile_picture=request.FILES.get('profile_picture')
                )
                
                messages.success(request, "Doctor registration successful! Please login.")
                return redirect('login')
            except Exception as e:
                user.delete()  # Rollback user creation if profile creation fails
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'register_doctor.html', {'form': form})

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create user first
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1']
                )
                
                # Create patient profile
                PatientProfile.objects.create(
                    user=user,
                    age=form.cleaned_data['age'],
                    medical_history=form.cleaned_data.get('medical_history', ''),
                    gender=form.cleaned_data.get('gender'),
                    contact_number=form.cleaned_data.get('contact_number'),
                    profile_picture=request.FILES.get('profile_picture')
                )
                
                messages.success(request, "Patient registration successful! Please login.")
                return redirect('login')
            except Exception as e:
                user.delete()  # Rollback user creation if profile creation fails
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'register_patient.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Try to get the user's doctor profile
            doctor_profile = DoctorProfile.objects.filter(user=user).first()
            if doctor_profile:
                return redirect('doctor_dashboard')
            
            # Try to get the user's patient profile
            patient_profile = PatientProfile.objects.filter(user=user).first()
            if patient_profile:
                return redirect('patient_dashboard')
            
            # If no profile exists
            messages.warning(request, 'No profile found. Please create a profile.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')



# Logout view
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime

from .models import Appointment, DoctorProfile, PatientProfile

@login_required
def doctor_dashboard(request):
    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('appointment_date', 'appointment_time')

        context = {
            'doctor_profile': doctor_profile,
            'appointments': appointments,
            'pending_appointments': appointments.filter(status='pending').count(),
            'confirmed_appointments': appointments.filter(status='confirmed').count(),
        }
        return render(request, 'doctor_dashboard.html', context)
    except DoctorProfile.DoesNotExist:
        messages.error(request, "You don't have permission to access the doctor dashboard.")
        return redirect('home')


@login_required
def patient_dashboard(request):
    try:
        patient_profile = PatientProfile.objects.get(user=request.user)
        appointments = Appointment.objects.filter(patient=request.user).order_by('appointment_date', 'appointment_time')

        context = {
            'patient_profile': patient_profile,
            'appointments': appointments,
            'pending_appointments': appointments.filter(status='pending').count(),
            'upcoming_appointments': appointments.filter(
                status='confirmed',
                appointment_date__gte=datetime.now().date()
            ),
        }
        return render(request, 'patient_dashboard.html', context)
    except PatientProfile.DoesNotExist:
        messages.error(request, "You don't have permission to access the patient dashboard.")
        return redirect('home')



# Appointment Booking View
from django.shortcuts import redirect
from .models import Appointment, DoctorProfile

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import Appointment, DoctorProfile, Report  # Import the new Report model

@login_required
def book_appointment(request):
    search_query = request.GET.get('search', '')

    # Filter doctors by name or specialization
    if search_query:
        doctors = (
            DoctorProfile.objects.filter(user__username__icontains=search_query)
            | DoctorProfile.objects.filter(specialization__icontains=search_query)
        )
    else:
        doctors = DoctorProfile.objects.all()

    if request.method == 'POST':
        selected_doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')
        medical_history = request.POST.get('medical_history')  # if using per-appointment history

        # Get any files from the request (could be multiple if <input type="file" multiple>)
        uploaded_files = request.FILES.getlist('reports')

        try:
            selected_doctor = DoctorProfile.objects.get(id=selected_doctor_id)

            # Create the appointment as unconfirmed
            appointment = Appointment.objects.create(
                doctor=selected_doctor,
                patient=request.user,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                is_confirmed=False,  # Initially unconfirmed
                status='pending',
                medical_history=medical_history or ""  # Ensure it's never None
            )

            # Save any uploaded files
            for f in uploaded_files:
                Report.objects.create(
                    appointment=appointment,
                    file=f
                )

            messages.success(request, "Appointment booked! Waiting for doctor confirmation.")
            return redirect('patient_dashboard')

        except DoctorProfile.DoesNotExist:
            messages.error(request, "The selected doctor does not exist.")

    return render(request, 'book_appointment.html', {
        'doctors': doctors,
        'search_query': search_query
    })




@login_required
def doctor_confirm_appointment(request, appointment_id):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)

    if request.method == 'POST':
        appointment.is_confirmed = True
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, 'Appointment confirmed successfully!')
        return redirect('doctor_dashboard')

    # Optional: If you want a confirmation page
    return render(request, 'confirm_appointment.html', {'appointment': appointment})

# views.py

import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Appointment

stripe.api_key = settings.STRIPE_SECRET_KEY  # Use your actual Stripe Secret Key

@login_required
def payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user, is_confirmed=True)

    if request.method == 'POST':
        # Grab the amount
        amount_str = request.POST.get('amount', '')
        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError("Invalid amount")
        except ValueError:
            messages.error(request, "Please enter a valid positive amount.")
            return redirect('payment', appointment_id=appointment_id)

        # Convert to cents
        stripe_amount = int(amount * 100)

        # Create Stripe Checkout Session (Server-side)
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Payment for Appointment #{appointment_id}",
                        },
                        'unit_amount': stripe_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('payment_success')),
                cancel_url=request.build_absolute_uri(reverse('payment_failure')),
            )
            # Redirect user to Stripe Checkout
            return redirect(checkout_session.url)
        except Exception as e:
            messages.error(request, f"Stripe error: {str(e)}")
            return redirect('payment', appointment_id=appointment_id)

    # GET request => show payment form
    return render(request, 'payment.html', {
        'appointment': appointment,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


@login_required
def payment_success(request):
    messages.success(request, "Your payment was successful!")
    # Optional: You can mark appointment as paid here if you want
    # But only do that after verifying the Stripe event if you want high integrity
    return redirect('home')  # or your success page

@login_required
def payment_failure(request):
    messages.error(request, "Payment was canceled or failed.")
    return redirect('home')  # or your retry page



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Appointment, Review
from .forms import ReviewForm

@login_required
def add_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    # Ensure the appointment is paid before allowing a review
    if not appointment.payment_status:
        messages.error(request, "You can only review paid appointments.")
        return redirect('home')

    # If a review already exists, optionally prevent duplicates:
    if hasattr(appointment, 'review'):
        messages.info(request, "You have already submitted a review for this appointment.")
        return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('home')
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'appointment': appointment
    }
    return render(request, 'add_review.html', context)




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