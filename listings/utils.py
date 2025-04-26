from django.core.mail import send_mail
from django.conf import settings
import csv
import os
from collections import defaultdict

# sends a welcome email to new users after signing up
def send_welcome_email(user):
    subject = 'Welcome to Our Car Website!'
    message = f'Hello {user.username},\n\nThank you for signing up for our car website. We are excited to have you on board!'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # sender email address (from settings.py)
        [user.email],  # receiver email
        fail_silently=False,  # raise an error if sending fails
    )

# loads car make and model data from a csv file into a dictionary
def load_make_model_data():
    csv_path = os.path.join(settings.BASE_DIR, 'listings', 'data', 'makes_models_updated.csv')  # path to the csv
    make_model_dict = {}
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            make = row['make']
            model = row['model']
            if make in make_model_dict:
                make_model_dict[make].append(model)  # add model to existing make
            else:
                make_model_dict[make] = [model]  # create new make entry
    return make_model_dict
