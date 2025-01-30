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

# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DoctorProfile, Appointment, Review
from django.contrib import messages

@login_required
def doctor_dashboard(request):
    # Assuming the logged-in user is a doctor
    try:
        doctor_profile = request.user.doctorprofile
    except DoctorProfile.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('home')

    # Fetch upcoming appointments (today and future)
    appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        appointment_date__gte=datetime.today(),
        status__in=['pending', 'confirmed']
    ).prefetch_related('reports')  # Prefetch related reports to optimize queries

    # Prefetch reviews to avoid N+1 queries
    reviews = Review.objects.filter(appointment__doctor=doctor_profile).select_related('appointment')

    context = {
        'doctor': doctor_profile,
        'appointments': appointments,
        'reviews': reviews,  # Optional if accessing via doctor.reviews.all
    }

    return render(request, 'doctor_dashboard.html', context)



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



import json
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from .models import Appointment

stripe.api_key = settings.STRIPE_SECRET_KEY  # Your Stripe secret key


@login_required
def payment(request, appointment_id):
    """
    Endpoint for rendering the payment page (GET) or
    creating a Stripe Checkout session (POST).
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user, is_confirmed=True)

    if request.method == 'POST':
        # Attempt to parse JSON data from the request body
        try:
            data = json.loads(request.body)
            amount_str = data.get('amount')
        except json.JSONDecodeError:
            # Fallback to form data if JSON parsing fails
            amount_str = request.POST.get('amount')
        
        # Validate the amount
        try:
            amount_value = float(amount_str)
            if amount_value <-1:
                return JsonResponse({"error": "Please enter a valid, positive amount."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid amount provided."}, status=400)

        # Convert dollars to cents
        amount_cents = int(round(amount_value * 100))

        # Create Stripe Checkout session
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Doctor Appointment Payment'},
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('payment_success')),
                cancel_url=request.build_absolute_uri(reverse('payment_failure')),
            )
            # (Optionally) Store appointment ID in session to retrieve after success
            request.session['appointment_id_for_review'] = appointment.id

            return JsonResponse({"checkout_url": session.url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # GET request: just render the payment form
    context = {
        'appointment': appointment,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payment.html', context)


@login_required
def payment_success(request):
    appointment_id = request.session.get("appointment_id_for_review")
    if appointment_id:
        # Retrieve the appointment from the DB
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Mark it as paid
        appointment.payment_status = True
        appointment.save()
    
    messages.success(request, "Your payment was successful!")
    return render(request, "payment_success.html", {"appointment_id": appointment_id})


def payment_failure(request):
    messages.error(request, "Payment failed. Please try again.")
    
    # If you have an appointment_id in session or as a URL param:
    appointment_id = request.session.get('appointment_id_for_review')  # or from the URL
    appointment = None

    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)
    
    return render(request, 'payment_failure.html', {'appointment': appointment})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Review
from .forms import ReviewForm

@login_required
def add_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    # Ensure the appointment is already paid
    if not appointment.payment_status:
        messages.error(request, "You can only review paid appointments.")
        return redirect('home')

    # Optional: If a review already exists, prevent duplicates
    # if hasattr(appointment, 'review'):
    #     messages.info(request, "You have already submitted a review for this appointment.")
    #     return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('home')  # Or some success page
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'add_review.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm

@login_required
def edit_review(request, review_id):
    """
    Allows a user to edit an existing review.
    """
    review = get_object_or_404(Review, id=review_id, appointment__patient=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated successfully!")
            return redirect('home')  # Redirect to dashboard or home page
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'edit_review.html', context)


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