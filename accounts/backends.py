from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CaseInsensitiveModelBackend(ModelBackend):
    """
    Custom authentication backend that allows case-insensitive email login.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(email__iexact=username.strip())
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email__iexact=username.strip()).first()
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
