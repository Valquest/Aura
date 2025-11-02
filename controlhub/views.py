from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from controlhub.models import User


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

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_reentry = request.POST.get('password_two')

        if username is '' or email is '':
            context = {
                'error': 'Must enter username and email'
            }
            return render(request, 'controlhub/register.html', context)

        if password != password_reentry:
            context = {
                'error': 'Passwords did not match.',
                'username': username,
                'email': email
            }
            return render(request, 'controlhub/register.html', context)
        
        user_exists_username = User.objects.filter(username=username).exists()
        user_exists_email = User.objects.filter(email=email).exists()
        if user_exists_username or user_exists_email:
            return render(request, 'controlhub/register.html', {'error': 'Username or Email already in use.'})
        
        print('doing this')
        new_user = User.objects.create_user(username=username, email=email, password=password)
        new_user.save()

        print('new user created')
        return redirect('login')

    return render(request, 'controlhub/register.html')