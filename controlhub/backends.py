from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom backend: Authenticates using either email or username.
    """
    def authenticate(self, request, username_email=None, password=None, **kwargs):
        if username_email is None:
            username_email = kwargs.get('username')
            username = ''
            email = ''
            if '@' in username_email:
                email = username_email
            else:
                username = username_email

        try:
            # Try username first, then email
            user = User.objects.get(Q(username=username) | Q(email=email))
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None
    
    def user_can_authenticate(self, user):
        # Ensure inactive users can't log in
        return user.is_active