from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class CustomAuthenticationModelBackend(ModelBackend):
    """
    Custom backend: Authenticates using either email or username.
    """
    def authenticate(self, request, username_email=None, password=None, **kwargs):
        if username_email is None:
            username_email = kwargs.get(User.USERNAME_FIELD or 'username')
        if username_email is None or password is None:
            return None
        
        username_email_lower = username_email.lower()

        if '@' in username_email_lower:
            query = Q(email__iexact=username_email_lower)
        else:
            query = Q(username__iexact=username_email_lower)

        try:
            user = User.objects.get(query)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def user_can_authenticate(self, user):
        # Ensure inactive users can't log in
        return user.is_active