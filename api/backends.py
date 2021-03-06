from django.contrib.auth.backends import ModelBackend

from .models import CustomUser


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = CustomUser
        try:
            user = UserModel.objects.get(email=kwargs['email'])
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
