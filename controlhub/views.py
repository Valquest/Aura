from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from controlhub.models import User, UserDeviceAccess, Device, DeviceAction, Stat

def active_devices(request):
    active_actions = DeviceAction.objects.filter(last_state="True")
    active_devices = {}
    for action in active_actions:
        if action.device.name not in active_devices:
            active_devices[action.device.name] = {
                'device': action.device,
                'count': 1
            }
        else:
            active_devices[action.device.name]['count'] += 1

    context = {
        'active_devices': active_devices,
    }
    return render(request, 'controlhub/active_devices.html', context)

def device_ctrl_page(request, device_id):
    
    device = Device.objects.get(id=device_id)
    
    # Define the Stat queryset without slicing
    stat_queryset = Stat.objects.order_by('-timestamp')
    device_actions = DeviceAction.objects.filter(device=device).prefetch_related(
        Prefetch(
            'stat_set',
            queryset=stat_queryset  # No slicing here
        )
    )
    return render(request, 'controlhub/device_ctrl_page.html', {
        'device_actions': device_actions,
        'device_name': device.name,
    })

def index(request):
    """
    Root url for logged in users
    """

    # If user is not logged in, redirect to a login page
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_access = UserDeviceAccess.objects.filter(user=request.user)
    print(user_access)

    context = {}
    context['devices'] = {}

    for access in user_access:
        device_name = Device.objects.get(id=access.device.id).name
        device_id = Device.objects.get(id=access.device.id).id

        context['devices'][device_id] = device_name

    return render(request, 'controlhub/index.html', context)

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
        
def logout_view(request):
    """
    Logout logic
    """
    logout(request)
    return redirect('login')


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