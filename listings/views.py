from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from .utils import load_make_model_data  
from .models import Car, Favorite, UserPreference, CarImage
from .forms import CarSearchForm, CarUploadForm, UserPreferenceForm, SignUpForm
import random



####################################### AUTHENTICATION AND USER REGISTRATION #####################################################

# login function

def sign_in(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('username')  # use email as username
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user:
                login(request, user) # logs user in
                return redirect(request.GET.get('next', 'car_list')) # redirects user to a specific page or the car_list page
            else:
                messages.error(request, "Invalid email or password")  # failed login

        else:
            messages.error(request, "Invalid email or password")  # form validation error

    return render(request, 'listings/login.html', {'form': form})

# logout function

def sign_out(request):
    logout(request)
    return redirect('login')  


# signup function

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # check if email is already in use
            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                return redirect('signup')

            try:
                user = User.objects.create_user(
                    username=email,  # use email as username
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.is_active = False  # prevent login until verified
                user.save()

                # Generate and store the PIN
                verification_pin = generate_pin()
                request.session['verification_pin'] = verification_pin
                request.session['user_id'] = user.id

                # Send the verification email
                send_verification_email(user, verification_pin)

                messages.success(request, "A 6-digit PIN has been sent to your email. Please verify to activate your account.")
                return redirect('verify_pin')  # Redirect to PIN verification page

            except IntegrityError:
                messages.error(request, "An error occurred. Please try again.")
                return redirect('signup')

    else:
        form = SignUpForm()

    return render(request, 'listings/signup.html', {'form': form})

def generate_pin():
    return str(random.randint(100000, 999999))  # Generate a 6 digit pin


# sends pin to users email
def send_verification_email(user, pin):
    subject = "Verify Your DriveTime Account"
    message = f"""
    Hi {user.first_name},

    Your 6-digit verification code is: {pin}

    Please enter this PIN on the website to complete your registration.

    Thank you for joining DriveTime!
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email], fail_silently=False)


# verify the pin entered by the user 

def verify_pin(request):
    if request.method == 'POST':
        entered_pin = request.POST.get('pin')
        stored_pin = request.session.get('verification_pin')
        user_id = request.session.get('user_id')

        if entered_pin == stored_pin:  
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True  # if the pin matches, activate the user
                user.save()

                # delete the pin and user_id from the session
                del request.session['verification_pin']
                del request.session['user_id']

                messages.success(request, "PIN verified successfully! You can now log in.")
                return redirect('login')

            except User.DoesNotExist:
                messages.error(request, "An error occurred. Please try again.")
                return redirect('signup')

        else:
            messages.error(request, "Incorrect PIN. Please try again.")

    return render(request, 'listings/verify_pin.html')

# resend a new pin to the user
@login_required
def resend_pin(request):
    user_id = request.session.get('user_id')  # Get user ID from session

    if not user_id:
        messages.error(request, "No user found to resend the PIN.")
        return redirect("login")  # Redirect to login if no user ID is found

    try:
        user = User.objects.get(id=user_id)  # Get the correct user
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("signup")  # Redirect if user not found

    new_pin = str(random.randint(100000, 999999))  # Generate a new 6 digit pin

    # Store the new pin in session
    request.session['verification_pin'] = new_pin  

    # Send the new pin via email
    send_mail(
        subject="Your New Verification PIN",
        message=f"Hello {user.first_name},\n\nHere is your new verification PIN: {new_pin}\n\nPlease use this to verify your account.",
        from_email="drivetime.noreply@gmail.com",
        recipient_list=[user.email],  
        fail_silently=False,
    )

    messages.success(request, f"A new PIN has been sent to {user.email}.")
    return redirect("verify_pin")  


def send_welcome_email(user):
    subject = 'Welcome to DriveTime, {}!'.format(user.first_name)
    message = f'Hi {user.username}! Thank you for signing up with DriveTime, we are excited to have you on board.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_email = user.email

    send_mail(subject, message, from_email, [recipient_email], fail_silently=False)

#########################################################################################################################

####################################### password reset ##################################################################

# handle password reset request form
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')  # get email from submitted form
        if email:
            try:
                user = User.objects.get(email=email)  # check if user with this email exists
            except User.DoesNotExist:
                return render(request, 'password_reset_error.html')  # show error page if not found

            # generate password reset link
            uid = urlsafe_base64_encode(str(user.pk).encode())
            token = default_token_generator.make_token(user)
            reset_url = f"{get_current_site(request).domain}/reset/{uid}/{token}/"

            # send password reset email
            subject = "Password Reset Request"
            message = f"Click the link to reset your password: {reset_url}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            
            return render(request, 'password_reset_done.html')  # confirmation page

    return render(request, 'password_reset_form.html')  # show password reset form

# handle actual password reset after clicking link
def reset_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()  # save new password
            update_session_auth_hash(request, user)  # keep user logged in
            return redirect('account_success')  # redirect to success page
    else:
        form = PasswordChangeForm(request.user)  # show password change form

    return render(request, 'listings/reset_password.html', {'form': form})

#########################################################################################################################


######################################## car views and management #######################################################

# list all cars with search, filtering, and sorting
def car_list(request):
    form = CarSearchForm(request.GET or None)
    filters = Q()
    favorites = []

    if request.user.is_authenticated:
        # get list of user's favourite car IDs
        favorites = list(Favorite.objects.filter(user=request.user).values_list('car_id', flat=True))

    # make dropdown always have 'Any' at the top
    form.fields['make'].choices = [('', 'Any')] + [(car['make'], car['make']) for car in Car.objects.values('make').distinct()]

    if request.method == 'GET' and request.GET:
        selected_make = request.GET.get('make', 'Any')
        selected_model = request.GET.get('model', 'Any')

        # set model choices based on selected make
        if selected_make != 'Any':
            form.fields['model'].choices = [('', 'Any')] + [(car['model'], car['model']) for car in Car.objects.filter(make__iexact=selected_make).values('model').distinct()]
        else:
            form.fields['model'].choices = [('', 'Any')] + [(car['model'], car['model']) for car in Car.objects.values('model').distinct()]

        if form.is_valid():
            # pull cleaned data from form
            query = form.cleaned_data.get('query', '')
            year = form.cleaned_data.get('year', 'Any')
            fuel_type = form.cleaned_data.get('fuel_type', 'Any')
            min_year = form.cleaned_data.get('min_year')
            max_year = form.cleaned_data.get('max_year')
            transmission = form.cleaned_data.get('transmission')
            min_mileage = form.cleaned_data.get('min_mileage')
            max_mileage = form.cleaned_data.get('max_mileage')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')

            # apply filters based on form input
            if query:
                filters |= Q(make__icontains=query) | Q(model__icontains=query)
            if year and year != 'Any':
                filters &= Q(year=year)
            if fuel_type and fuel_type != 'Any':
                filters &= Q(fuel_type__iexact=fuel_type)
            if selected_make and selected_make != 'Any':
                filters &= Q(make__iexact=selected_make)
            if selected_model and selected_model != 'Any':
                filters &= Q(model__iexact=selected_model)
            if min_year and min_year != 'Any':
                filters &= Q(year__gte=min_year)
            if max_year and max_year != 'Any':
                filters &= Q(year__lte=max_year)
            if transmission and transmission != 'Any':
                filters &= Q(transmission__iexact=transmission)
            if min_mileage and min_mileage != 'Any':
                filters &= Q(mileage__gte=int(min_mileage))
            if max_mileage and max_mileage != 'Any':
                filters &= Q(mileage__lte=int(max_mileage))
            if min_price and min_price != 'Any':
                filters &= Q(price__gte=int(min_price))
            if max_price and max_price != 'Any':
                filters &= Q(price__lte=int(max_price))

    # sorting results
    sort_by = request.GET.get('sort_by', 'newest')
    cars = Car.objects.filter(filters)

    if sort_by == 'lowest_price':
        cars = cars.order_by('price')
    elif sort_by == 'highest_price':
        cars = cars.order_by('-price')
    elif sort_by == 'oldest':
        cars = cars.order_by('year')
    elif sort_by == 'newest':
        cars = cars.order_by('-year')
    elif sort_by == 'lowest_mileage':
        cars = cars.order_by('mileage')

    return render(request, 'listings/car_list.html', {
        'form': form,
        'cars': cars,
        'favorites': favorites,
        'selected_sort': sort_by
    })

# view car detail page and track views
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    is_favorite = False

    if request.user.is_authenticated:
        if request.user != car.user:
            car.views += 1  # only count view if user isn't the car owner
            car.save()
        is_favorite = Favorite.objects.filter(user=request.user, car=car).exists()
    else:
        car.views += 1  # anonymous users views are counted too
        car.save()

    return render(request, 'listings/car_detail.html', {
        'car': car,
        'is_favorite': is_favorite
    })

# upload a new car
def upload_car(request):
    make_model_data = load_make_model_data()  # load makes and models from csv

    if request.method == 'POST':
        form = CarUploadForm(request.POST or None, request.FILES or None)

        # manually add dropdown fields
        form.fields['year'] = forms.ChoiceField(
            choices=[('', 'Select Year')] + [(year, year) for year in range(2025, 1989, -1)],
            required=True,
            label='Year'
        )
        form.fields['fuel_type'] = forms.ChoiceField(
            choices=[('', 'Select Fuel Type')] + [
                ('Petrol', 'Petrol'),
                ('Diesel', 'Diesel'),
                ('Electric', 'Electric'),
                ('Hybrid', 'Hybrid')
            ],
            required=True,
            label='Fuel Type'
        )
        form.fields['engine_size'] = forms.ChoiceField(
            choices=[('', 'Select Engine Size')] + [
                (f"{x:.1f}", f"{x:.1f}L") for x in [round(i * 0.1, 1) for i in range(10, 81)]
            ],
            required=True,
            label='Engine Size'
        )
        form.fields['number_of_doors'] = forms.ChoiceField(
            choices=[('', 'Select Number of Doors')] + [
                ('2', '2 doors'),
                ('3', '3 doors'),
                ('4', '4 doors'),
                ('5', '5 doors')
            ],
            required=True,
            label='Number of Doors'
        )

        if form.is_valid():
            # validate make/model relationship
            make = form.cleaned_data['make']
            model = form.cleaned_data['model']
            if make not in make_model_data or model not in make_model_data[make]:
                form.add_error('model', 'Selected model is not valid for the chosen make.')
            else:
                car = form.save(commit=False)
                car.user = request.user
                car.save()

                # save uploaded images
                images = request.FILES.getlist('images')
                for img in images:
                    CarImage.objects.create(car=car, image=img)

                return redirect('car_list')

    else:
        form = CarUploadForm()

        # same dropdowns if GET
        form.fields['year'] = forms.ChoiceField(
            choices=[('', 'Select Year')] + [(year, year) for year in range(2025, 1989, -1)],
            required=True,
            label='Year'
        )
        form.fields['fuel_type'] = forms.ChoiceField(
            choices=[('', 'Select Fuel Type')] + [
                ('Petrol', 'Petrol'),
                ('Diesel', 'Diesel'),
                ('Electric', 'Electric'),
                ('Hybrid', 'Hybrid')
            ],
            required=True,
            label='Fuel Type'
        )
        form.fields['engine_size'] = forms.ChoiceField(
            choices=[('', 'Select Engine Size')] + [
                (f"{x:.1f}", f"{x:.1f}L") for x in [round(i * 0.1, 1) for i in range(10, 81)]
            ],
            required=True,
            label='Engine Size'
        )
        form.fields['number_of_doors'] = forms.ChoiceField(
            choices=[('', 'Select Number of Doors')] + [
                ('2', '2 doors'),
                ('3', '3 doors'),
                ('4', '4 doors'),
                ('5', '5 doors')
            ],
            required=True,
            label='Number of Doors'
        )

    return render(request, 'listings/upload_car.html', {
        'form': form,
        'make_model_data': make_model_data
    })

# delete a car
def remove_car(request, car_id):
    if request.method == "POST":
        car = get_object_or_404(Car, id=car_id, user=request.user)  # ensure user owns car
        car.delete()
        return redirect('my_cars')

# show logged in user's cars
def my_cars(request):
    if request.user.is_authenticated:
        cars = Car.objects.filter(user=request.user)
        return render(request, 'listings/my_cars.html', {'cars': cars})
    else:
        return redirect('login')

###############################################################################################################################

################################################ FAVOURITES ######################################################################

def add_favorite(request, car_id):
    car = get_object_or_404(Car, id=car_id)  # get the car or return 404 if it doesnt exist
    if request.user.is_authenticated:  # only allow logged in users to favourite cars
        Favorite.objects.get_or_create(user=request.user, car=car)  # create favourite if it doesnt already exist
    return redirect('car_list')  # after adding, go back to the car list

def remove_favorite(request, car_id):
    car = get_object_or_404(Car, id=car_id)  # get the car or return 404
    if request.user.is_authenticated:  # only allow logged in users
        Favorite.objects.filter(user=request.user, car=car).delete()  # delete the favourite link
    return redirect('car_list')  # after removing, go back to the car list

def favorite_cars(request):
    if request.user.is_authenticated:
        # get all favourites for the logged in user, and fetch related car objects efficiently
        favorites = Favorite.objects.filter(user=request.user).select_related('car')
    else:
        favorites = []  # if not logged in, no favourites

    return render(request, 'listings/favorite_cars.html', {'favorites': favorites})


####################################### ACCOUNT MANAGEMENT AND RECOMMENDATIONS #####################################################################

def recommend_cars(user):
    preferences = user.userpreference
    recommendations = Car.objects.all()

    # normalize string fields (lowercase, remove extra spaces)
    transmission = preferences.transmission.strip().lower() if preferences.transmission else None
    fuel_type = preferences.fuel_type.strip().lower() if preferences.fuel_type else None

    # apply filters based on user preferences
    if preferences.min_year is not None:
        recommendations = recommendations.filter(year__gte=preferences.min_year)

    if preferences.max_year is not None:
        recommendations = recommendations.filter(year__lte=preferences.max_year)

    if preferences.min_mileage is not None:
        recommendations = recommendations.filter(mileage__gte=preferences.min_mileage)

    if preferences.max_mileage is not None:
        recommendations = recommendations.filter(mileage__lte=preferences.max_mileage)

    if preferences.doors is not None:
        recommendations = recommendations.filter(number_of_doors=preferences.doors)

    if transmission:
        recommendations = recommendations.filter(transmission__iexact=transmission)  # case insensitive match

    if fuel_type:
        recommendations = recommendations.filter(fuel_type__iexact=fuel_type)

    if preferences.min_price is not None:
        recommendations = recommendations.filter(price__gte=preferences.min_price)

    if preferences.max_price is not None:
        recommendations = recommendations.filter(price__lte=preferences.max_price)

    return recommendations

def recommend_cars_view(request):
    recommendations = []

    if request.user.is_authenticated:
        # make sure the user has a UserPreference object or create it if its missing
        preference, created = UserPreference.objects.get_or_create(user=request.user)

        # now safe to recommend cars
        recommendations = recommend_cars(request.user)

    return render(request, 'listings/recommended_cars.html', {'recommendations': recommendations})

@login_required
def reset_preferences(request):
    # delete users preferences completely
    UserPreference.objects.filter(user=request.user).delete()
    messages.success(request, "Preferences have been reset.")
    return redirect('account_details')

@login_required
def account_details(request):
    if request.method == 'POST':
        preferences, _ = UserPreference.objects.get_or_create(user=request.user)
        action = request.POST.get('action')

        if action == 'reset':
            # reset all fields to empty
            preferences.fuel_type = None
            preferences.transmission = None
            preferences.min_price = None
            preferences.max_price = None
            preferences.min_mileage = None
            preferences.max_mileage = None
            preferences.min_year = None
            preferences.max_year = None
            preferences.doors = None
            preferences.save()
            messages.success(request, "Vehicle preferences have been reset.")
            return redirect('account_details')

        elif action == 'save':
            # save preferences from submitted form
            preferences.fuel_type = request.POST.get('fuel_type').strip().lower() if request.POST.get('fuel_type') and request.POST.get('fuel_type') != "Any" else None
            preferences.transmission = request.POST.get('gearbox_type').strip().lower() if request.POST.get('gearbox_type') and request.POST.get('gearbox_type') != "Any" else None

            min_price_val = request.POST.get('min_price')
            preferences.min_price = float(min_price_val) if min_price_val not in [None, '', 'Any'] else None

            max_price_val = request.POST.get('max_price')
            preferences.max_price = float(max_price_val) if max_price_val not in [None, '', 'Any'] else None

            preferences.min_mileage = None if request.POST.get('min_mileage') == "Any" else (int(request.POST.get('min_mileage')) if request.POST.get('min_mileage') else None)
            preferences.max_mileage = None if request.POST.get('max_mileage') == "Any" else (int(request.POST.get('max_mileage')) if request.POST.get('max_mileage') else None)
            preferences.min_year = None if request.POST.get('min_year') == "Any" else (int(request.POST.get('min_year')) if request.POST.get('min_year') else None)
            preferences.max_year = None if request.POST.get('max_year') == "Any" else (int(request.POST.get('max_year')) if request.POST.get('max_year') else None)
            preferences.doors = request.POST.get('doors') if request.POST.get('doors') and request.POST.get('doors') != "Any" else None

            preferences.save()
            return redirect('account_details')

    # if GET, show form with current preferences
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)

    # set up dropdown options
    year_choices = list(range(2000, 2026))
    mileage_choices = list(range(0, 100001, 10000))
    price_choices = list(range(1000, 100001, 1000))
    doors_choices = [2, 3, 4, 5]
    gearbox_choices = ['manual', 'automatic']
    fuel_choices = ['petrol', 'diesel', 'electric', 'hybrid petrol']

    # add 'Any' at the start of each list
    year_choices.insert(0, 'Any')
    mileage_choices.insert(0, 'Any')
    price_choices.insert(0, 'Any')
    doors_choices.insert(0, 'Any')
    gearbox_choices.insert(0, 'Any')
    fuel_choices.insert(0, 'Any')

    # get recommended cars based on saved preferences
    recommendations = recommend_cars(request.user)

    return render(request, 'listings/account_details.html', {
        'user': request.user,
        'preferences': preferences,
        'recommendations': recommendations,
        'year_choices': year_choices,
        'mileage_choices': mileage_choices,
        'price_choices': price_choices,
        'doors_choices': doors_choices,
        'gearbox_choices': gearbox_choices,
        'fuel_choices': fuel_choices,
    })

def update_preferences(request):
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=request.user.userpreference)
        if form.is_valid():
            form.save()
            return redirect('account_details')  # after saving, go back to account details
    else:
        form = UserPreferenceForm(instance=request.user.userpreference)

    return render(request, 'listings/update_preferences.html', {'form': form})


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

