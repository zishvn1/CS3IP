from django.db import models
from django.contrib.auth.models import User

# stores user preferences for recommended cars
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fuel_type = models.CharField(max_length=50, null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_mileage = models.PositiveIntegerField(null=True, blank=True)
    max_mileage = models.PositiveIntegerField(null=True, blank=True)
    doors = models.PositiveIntegerField(null=True, blank=True)
    transmission = models.CharField(max_length=50, null=True, blank=True)
    min_year = models.PositiveIntegerField(null=True, blank=True)
    max_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s preferences"

# links a user to their favourite cars
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey('listings.Car', on_delete=models.CASCADE)  # string reference for car model

    class Meta:
        unique_together = ('user', 'car')  # a user cant favourite the same car twice

# main car model for listings
class Car(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    model_variant = models.CharField(max_length=100, blank=True)
    year = models.IntegerField()
    mileage = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=50)
    engine_size = models.DecimalField(max_digits=3, decimal_places=1)
    transmission = models.CharField(max_length=20, choices=[('manual', 'Manual'), ('automatic', 'Automatic')], default='manual')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user who uploaded the car
    image = models.ImageField(upload_to='car_images/', blank=True)  # thumbnail image
    views = models.PositiveIntegerField(default=0)  # how many times viewed
    number_of_doors = models.IntegerField(default=1)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.make} {self.model}({self.year})"

# stores vehicle preference info 
class VehiclePreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doors = models.IntegerField(null=True, blank=True)
    gearbox_type = models.CharField(max_length=20, choices=[('manual', 'Manual'), ('automatic', 'Automatic')], null=True, blank=True)
    fuel_type = models.CharField(max_length=20, choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric')], null=True, blank=True)
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s Preferences"

# adds a member number field to each user 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_number = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

# supports multiple images per car listing
class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='car_images/')
