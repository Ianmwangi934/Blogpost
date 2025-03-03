from django.shortcuts import render,get_object_or_404,redirect
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile,Airlines,Booking
from django.contrib.auth.decorators import login_required
import requests
class LoginForm(forms.Form):
    username = forms.CharField(label="username", widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    email = forms.CharField(label="email", widget=forms.TextInput(attrs={'placeholder':'Enter your email'}))
    password = forms.CharField(label="password", widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
class NewUserForm(forms.Form):
    username = forms.CharField(label="username", widget=forms.TextInput(attrs={'placeholder': 'Enter your Username'}))
    email = forms.CharField(label="email", widget=forms.TextInput(attrs={'placeholder':'Enter your email'}))
    password = forms.CharField(label="password",widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
class ProfileForm(forms.Form):
    first_name = forms.CharField(label="first_name", widget=forms.TextInput(attrs={'placeholder':'Your First name'}))
    middle_name = forms.CharField(label="middle_name", widget=forms.TextInput(attrs={'placeholder':'Your middle name'}))
    last_name = forms.CharField(label="last_name", widget=forms.TextInput(attrs={'placeholder':'Your Last name'}))
    customer_id = forms.CharField(label="customer_id",widget=forms.TextInput(attrs={'placeholder':'Your National id'}))
    passport_number = forms.CharField(label="passport_number", widget=forms.TextInput(attrs={'placeholder': 'Your passport number'}))
    photo = forms.ImageField(label="photo", required=False)

# Create your views here.
@login_required()
def book_flight_view(request):
    if request.method == "POST":
        #Retrieving flight data from the form submission
        flight_number = request.POST.get('flight_number')
        departure_airport = request.POST.get('departure_airport')
        arrival_airport = request.POST.get('arrival_airport')
        airline_iata = request.POST.get('airline_iata')

        #Looking up the airline from our database
        airline = get_object_or_404(Airlines, iata_code=airline_iata)

        #creating the booking record
        booking = Booking.objects.create(
            user = request.user,
            airline = airline,
            flight_number=flight_number,
            departure_airport=departure_airport,
            arrival_airport=arrival_airport
        )
        return render(request, "customer/booking_confirmation.html",{
            "booking":booking
        })
    else:
        #For get request, we assume the flight details are passed as  query parameters
        flight_number = request.GET.get('flight_number')
        departure_airport = request.GET.get('departure_airport')
        arrival_airport = request.GET.get('arrival_airport')
        airline_iata = request.GET.get('airline_iata')
        context = {
            "flight_number":flight_number,
            "departure_airport":departure_airport,
            "arrival_airport":arrival_airport,
            "airline_iata":airline_iata,
        }
        return render(request, "customer/book_flight.html", context)
def airlines(request):
    airlines = Airlines.objects.all()
    print(airlines)
    return render(request, "customer/airline.html",{
        "airlines":airlines
    })
def airline_detail(request,airline_id):
    airline = get_object_or_404(Airlines, id=airline_id)
    return render(request, "customer/airline_detail.html",{
        "airline":airline
    })
def flight_data_view(request, iata_code):
    #Retrieving the airline object by id
    airline = get_object_or_404(Airlines, iata_code=iata_code)
    #Building the API endpoint using the airline's IATA code.
    endpoint = (
        f"http://api.aviationstack.com/v1/flights?"
        f"access_key=294b13ef1053bb49e6294514be8567e4&airline_iata={iata_code}"
    )
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        flight_data = response.json().get("data",[])
    except requests.RequestException as e:
        flight_data = {"error": str(e)}
    return render(request, "customer/flight_data.html",{
        "airline":airline,
        "flight_data":flight_data
    })
def profile_view(request,username):
    user = get_object_or_404(User,username=username)

    #create the user profile
    profile, create = Profile.objects.get_or_create(user=user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES) #handling both text and files(images)
        if form.is_valid():
            profile.first_name = form.cleaned_data["first_name"]
            profile.middle_name = form.cleaned_data["middle_name"]
            profile.last_name = form.cleaned_data["last_name"]
            profile.customer_id = form.cleaned_data["customer_id"]
            profile.passport_number = form.cleaned_data["passport_number"]

            if form.cleaned_data["photo"]:
                profile.photo = form.cleaned_data["photo"]
            profile.save()

            #redirect the customer to the profile page after saving the profile
            return HttpResponseRedirect(reverse("profile_view", args=[user.username]))
        else:
            #if the form is not valid, re render the form with errors
            return render(request, "customer/create_profile.html",{
                "form":form
            })
    else:
        #customer already has profile data
        if not profile.first_name or not profile.middle_name or not profile.last_name or not profile.customer_id or not profile.passport_number or not profile.photo:
            #user is new or hasen't filled in profile data
            form = ProfileForm()
            return render(request, "customer/create_profile.html",{
                "form":form
            })

        else:
            #user already has profile data, show the data
            form = ProfileForm(initial={
                'first_name':profile.first_name,
                'middle_name':profile.middle_name,
                'last_name':profile.last_name,
                'customer_id':profile.customer_id,
                'passport_number':profile.passport_number,
                'photo':profile.photo
            })
            return render(request, "customer/profile.html",{
                "profile":profile
            })
    


def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login_view"))
    return render(request, "customer/home.html")
def login_view(request):
    form = LoginForm()
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse(airlines))
        else:
            return HttpResponseRedirect(reverse("signup"))
    return render(request, "customer/login.html",{
        "form":form
    })

def signup(request):
    form = NewUserForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            #create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            #login the user
            login(request,user)
            return HttpResponseRedirect(reverse("profile_view", args=[user.username]))

        else:
            return render (request, "customer/signup.html",{
                "form":form
            })
    return render(request, "customer/signup.html",{
        "form":form
    })


         
