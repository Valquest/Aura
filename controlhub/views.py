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
    if request.method == 'GET':
        return render(request, 'controlhub/login.html')
    
    if request.method == 'POST':
        print("Doing this")
        username_email = request.POST.get('username_email')
        password = request.POST.get('password')
        print(username_email)
        print(password)
        print("Trying to authenticate")
        user = authenticate(username=username_email, password=password)
        print(f'User: {user}')
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            print("User is None")
            context = {
                'error': 'User does not exist or your password is incorrect',
                'username_email': username_email
            }
            return render(request, 'controlhub/login.html', context)
        
def register(request):
    pass