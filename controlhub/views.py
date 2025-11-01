from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect('authenticate')
    return render(request, 'controlhub/index.html')

def authenticate(request):
    return render(request, 'controlhub/login.html')