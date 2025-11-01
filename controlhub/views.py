from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse


def index(request):
    """
    Root url for logged in users
    """

    # If user is not logged in, redirect to a login page
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'controlhub/index.html')

def login_view(request):
    """
    Authentication page view
    """
    if request.method == 'POST':
        username_email = request.POST.get('username_email')
        password = request.POST.get('password')

        username_email = (username_email or '').strip()

        user = authenticate(username=username_email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            context = {
                'error': 'User does not exist or your password is incorrect',
                'username_email': username_email
            }
            return render(request, 'controlhub/login.html', context)
    
    return render(request, 'controlhub/login.html')
        
def register(request):
    pass