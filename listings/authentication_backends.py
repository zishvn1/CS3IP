from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

# custom authentication backend to allow login with email instead of username
class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # try to find a user with the given email (username passed will be email)
            user = User.objects.get(email=username)
            # check if the password matches
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # if user is not found, return None
            return None
