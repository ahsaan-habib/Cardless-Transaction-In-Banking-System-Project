from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

user_model = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, email_or_phone, username=None, password=None, **kwargs):

        users = user_model._default_manager.filter(
            Q(phone__iexact=email_or_phone) | Q(email__iexact=email_or_phone)
        )

        # Test whether any matched user has the provided password:
        for user in users:
            if user.check_password(password):
                return user
        if not users:
            user_model().set_password(password)

    def get_user(self, user_id):
        try:
            user = user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
