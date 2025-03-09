from django.shortcuts import render, redirect
from accounts.models import *
from core.models import *
from payment.models import *

# Create your views here.

def homepage(request):
    cities = city.objects.all()
    user = None
    # featured_rooms = Room.objects.all().order_by("-id")[:4]


    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type != 'customer':  
            return redirect('login')
        
        # featured_rooms = Room.objects.all().order_by("-id")[:4]


    data = {
        'user': user,
        'cities': cities,
        # 'featured_rooms': featured_rooms,
    }
    return render(request, "core/homepage.html", data)
