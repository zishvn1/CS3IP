from django import forms
from .models import Car, VehiclePreference, UserPreference
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Min, Max
from django.core.exceptions import ValidationError

# custom signup form
class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Enter your first name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Enter your last name")
    email = forms.EmailField(required=True, help_text="Enter a valid email address")
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    # validate that email is unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use, please choose another email.")
        return email

# custom user creation form (can extend if needed)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

# form for updating or creating user preferences
class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['fuel_type', 'min_price', 'max_price', 'min_mileage', 'max_mileage', 'doors', 'transmission', 'min_year', 'max_year']

# car search form with dynamic fields
class CarSearchForm(forms.Form):
    # static choice fields
    fuel_type = forms.ChoiceField(choices=[
        ('', 'Any'),
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ], required=False)

    make = forms.ChoiceField(choices=[], required=False)
    model = forms.ChoiceField(choices=[], required=False)
    min_year = forms.ChoiceField(choices=[], required=False, label='Min Year')
    max_year = forms.ChoiceField(choices=[], required=False, label='Max Year')
    transmission = forms.ChoiceField(choices=[
        ('', 'Any'),
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ], required=False)

    min_mileage = forms.ChoiceField(choices=[], required=False, label='Min Mileage')
    max_mileage = forms.ChoiceField(choices=[], required=False, label='Max Mileage')
    min_price = forms.ChoiceField(choices=[], required=False, label='Min Price')
    max_price = forms.ChoiceField(choices=[], required=False, label='Max Price')

    # predefined year choices
    year_choices = [(year, year) for year in range(2000, 2025)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # populate make dropdown from database
        makes = list(Car.objects.values_list('make', flat=True).distinct())
        makes = sorted(set(makes) - {''})
        self.fields['make'].choices = [('', 'Any')] + [(make, make) for make in makes]

        # populate year dropdowns
        self.fields['min_year'].choices = [('', 'Any')] + self.year_choices
        self.fields['max_year'].choices = [('', 'Any')] + self.year_choices

        # populate mileage dropdowns dynamically
        if Car.objects.exists():
            min_mileage = Car.objects.aggregate(Min('mileage'))['mileage__min']
            max_mileage = Car.objects.aggregate(Max('mileage'))['mileage__max']

            rounded_min = (int(min_mileage) // 10000) * 10000 if min_mileage else 0
            rounded_max = ((int(max_mileage) // 10000) + 1) * 10000 if max_mileage else 10000

            mileage_choices = [(str(i), str(i)) for i in range(rounded_min, rounded_max + 1, 10000)]
            self.fields['min_mileage'].choices = [('', 'Any')] + mileage_choices
            self.fields['max_mileage'].choices = [('', 'Any')] + mileage_choices

        # populate price dropdowns dynamically
        if Car.objects.exists():
            min_price = Car.objects.aggregate(Min('price'))['price__min']
            max_price = Car.objects.aggregate(Max('price'))['price__max']

            rounded_min = (int(min_price) // 10000) * 10000 if min_price else 0
            rounded_max = ((int(max_price) // 10000) + 1) * 10000 if max_price else 10000

            price_choices = [(str(i), str(i)) for i in range(rounded_min, rounded_max + 1, 10000)]
            self.fields['min_price'].choices = [('', 'Any')] + price_choices
            self.fields['max_price'].choices = [('', 'Any')] + price_choices


        self.fields['model'].choices = [('', 'Any')]  # model will be dynamically filled by javascript

# vehicle preferences form for users
class VehiclePreferenceForm(forms.ModelForm):
    class Meta:
        model = VehiclePreference
        fields = ['doors', 'gearbox_type', 'fuel_type', 'price_range_min', 'price_range_max']

# car upload form
class CarUploadForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'mileage', 'fuel_type', 'engine_size', 'transmission', 'price', 'image', 'number_of_doors', 'phone_number', 'city']
