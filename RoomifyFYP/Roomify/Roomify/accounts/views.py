from django.shortcuts import render, redirect
from accounts.models import User, city
from payment.models import Subscription, Payment
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
import requests
from datetime import datetime, timedelta
import uuid
import json


def register_option(request):
    return render(request, "registration/register_option.html")

def customer_register(request):
    # fetching city data
    cities = city.objects.all() 

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower()
        phone = request.POST.get("phone")
        city_id = request.POST.get("city")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if password == confirm_password:
            # check phone exist or not
            if get_user_model().objects.filter(phone=phone).exists():
                messages.error(request, "Phone Number already taken")
                return redirect("customer_register")
            
            # Check if the email already exists
            if get_user_model().objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('customer_register')
            
            city_obj = city.objects.filter(id=city_id).first() if city_id else None
            
            user = get_user_model().objects.create_user(
                email=email,
                name=name,
                phone = phone,
                city=city_obj,
                password=password,
                user_type='customer'
            )
            user.save()
            messages.success(request, "Account Created Success")
            return redirect("login")
        else:
            messages.error(request, "Passwords and Confirm Password need to match!")
            return redirect('customer_register')

    return render(request, "registration/customer_register.html",{'cities':cities})


def seller_register(request):
        # Fetch city data
    cities = city.objects.all()
    
    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower()
        phone = request.POST.get("phone")
        city_id = request.POST.get("city", "")
        photo = request.FILES.get("photo")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            messages.error(request, "Passwords and Confirm Password need to match!")
            return redirect('seller_register')

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone Number already taken")
            return redirect("seller_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("seller_register")
        purchase_order_id = str(uuid.uuid4())  # Generate a unique ID

        url = "https://dev.khalti.com/api/v2/epayment/initiate/"

        payload = json.dumps({
            "return_url": "http://127.0.0.1:8000/verify_payment",
            "website_url": "http://127.0.0.1:8000/",
            "amount": 1100 * 100,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Seller Subscription",
        })
        headers = {
            'Authorization': 'key 0b7fa0b9a2bc40299d1b91329ff8fe63',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, data=payload)
        print(response.text)
        response_data = response.json()

        print("khalti api response:", response_data)
        print(response.status_code)


        if response.status_code == 200 :
            request.session['temp_user'] = json.dumps(
                {
                'name': name,
                'email': email,
                'phone': phone,
                'city_id': city_id,
                'photo': photo.name if photo else None,
                'password': password,
                }
            ) 
            # Save image temporarily
            if photo:
                file_path = f"img/user_img/{photo.name}"
                default_storage.save(file_path, photo)

            print("session data stored:", request.session['temp_user'])
            return redirect(response_data['payment_url'])
    return render(request, "registration/seller_register.html",{'cities':cities})

def seller_register_verify(request):
    lookup_url = "https://dev.khalti.com/api/v2/epayment/lookup/" 
    
    if request.method == 'GET':
        headers = {
            'Authorization': 'key 0b7fa0b9a2bc40299d1b91329ff8fe63',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        print("pidx:", pidx)
        print("headers:", headers)

        data = json.dumps({
            'pidx': pidx
        })
        response = requests.post(lookup_url, headers=headers, data=data)
        print(response.text)

        new_response = json.loads(response.text)
        print(new_response)

        transaction_id = new_response.get('transaction_id', 'unkown transaction')
        print("transaction_id:", transaction_id)
        print(response.status_code)
        print(new_response['status'])

        # if response.status_code == 200:
        if new_response['status'] == 'Completed':
            temp_user = request.session.get('temp_user')
            print(temp_user)
            if not temp_user:
                messages.error(request, "Session expired. Try again.")
                return redirect('seller_register')
            else:
                    temp_user = json.loads(temp_user)  # Convert JSON string to dictionary

                    city_obj = city.objects.filter(id=temp_user.get('city_id')).first() if temp_user.get('city_id') else None
                    print(city_obj)
                    
                    start_date = datetime.now()
                    end_date = start_date + timedelta(days=30)
                    
                    user = User.objects.create_user(
                        email=temp_user.get('email'),
                        name=temp_user.get('name'),
                        phone=temp_user.get('phone'),
                        city=city_obj,
                        password=temp_user.get('password'),
                        # user_image=temp_user.get('photo', None),
                        user_type='seller',
                        is_subscribed=True,
                        subscription_end_date=end_date,
                    )
                    # Assign the saved image to the user
                    if temp_user.get('photo'):
                        user.user_image = f"img/user_img/{temp_user['photo']}"
                        user.save()

                    Subscription.objects.create(
                        seller=user, 
                        transaction_id=transaction_id,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=True
                    )
                    payment_date = datetime.now()
                    Payment.objects.create(
                        seller=user, 
                        amount= 1500, 
                        transaction_id=transaction_id,
                        payment_date=payment_date,
                        status='success'
                    )
                    user.save()
                    messages.success(request, "Payment Successful... Account Created")
                    return redirect("login")

        else:
            messages.error(request, f"Payment verification failed: {new_response.get('detail', 'Unknown error.')}")
            return redirect('seller_register')

def login_user(request):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            user = authenticate(request, username=email, password=password)

            if user:
                login(request, user)

                if user.user_type == "seller":
                    return redirect("seller_dashboard")
                elif user.user_type == "customer":
                    return redirect("homepage")
                else:
                    messages.error(request, "Didnt Found Account")
                    return redirect("login")
            else:
                messages.error(request, "Invalid username or password")
                return redirect("login")
        return render(request, "registration/login.html")

def logout_user(request):
    logout(request)
    return redirect('homepage')

def Subscription_renew(request):
    if request.method == "POST":
        # generate unique purchase id
        purchase_order_id = str(uuid.uuid4())

        url = "https://dev.khalti.com/api/v2/epayment/initiate/"

        payload = json.dumps({
            "return_url": "http://127.0.0.1:8000/verify_renewal",
            "website_url": "http://127.0.0.1:8000/",
            "amount": 1200 * 100,   
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Subscription Renewal",
        })

        headers = {
            'Authorization': 'key 0b7fa0b9a2bc40299d1b91329ff8fe63',
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, data=payload)
        print(response.text)

        # Store renewal intent in session
        request.session['renewal_detail'] = {
            'seller_id': request.user.id,
            'purchase_order_id': purchase_order_id
        }

        if response.status_code == 200:
            response_data = response.json()
            return redirect(response_data['payment_url'])
        else:
            messages.error(request, "Payment Fail Status Code not 200!!. Please try again.")
            return redirect('seller_dashboard') 
        


def verify_renewal(request):
    
    lookup_url = "https://dev.khalti.com/api/v2/epayment/lookup/" 

    if request.method == 'GET':
        headers = {
            'Authorization': 'key 0b7fa0b9a2bc40299d1b91329ff8fe63',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')

        data = json.dumps({
            'pidx': pidx
        })
        response = requests.post(lookup_url, headers=headers, data=data)
        new_response = json.loads(response.text)

        transaction_id = new_response.get('transaction_id', 'unkown transaction')

        if new_response['status'] == 'Completed':
            renewal_detail = request.session.get('renewal_detail')
            if not renewal_detail:
                messages.error(request, "Session expired. Try again.")
                return redirect('seller_dashboard') 
            
            seller = request.user
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)

            # Update subscription
            seller.is_subscribed = True
            seller.subscription_end_date = end_date
            seller.save()

            # Create Subscription records
            Subscription.objects.create(
                seller=seller, 
                transaction_id=transaction_id,
                start_date=start_date,
                end_date = end_date,
                is_active=True
            )
            payment_date = datetime.now()
            Payment.objects.create(
                seller=seller,
                amount= 1100,
                transaction_id=transaction_id,
                payment_date = payment_date,
                status='success',
                title='Renew Subscription'
            )
            seller.save()
            messages.success(request, "Renew Account Successful.. Thank You")
            return redirect('seller_dashboard') 
        else:
            messages.error(request, f"Payment Canceled")
            return redirect('seller_dashboard') 
    else:
        messages.error(request, f"Payment verification failed: {new_response.get('detail', 'Unknown error.')}")
        return redirect('seller_dashboard')