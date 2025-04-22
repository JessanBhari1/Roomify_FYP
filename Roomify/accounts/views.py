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
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from Roomify import settings
from accounts.validation import password_validation


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
            
            if len(phone)!= 10 or not phone.isdigit():
                messages.error(request, "Phone Number must be 10 digits and contain number only")
                return redirect('customer_register')
            
            # Validate password
            errors = password_validation(password)
            if errors:
                messages.error(request, errors[0])
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
            # Send verification email
            mail_subject = 'Activate your account'
            email_template = 'registration/verification_email.html'
            if send_verification_email(request, user, mail_subject, email_template):
                messages.success(request, "Account created successfully! Please check your email to activate your account.")
                return redirect("customer_register")

            else:
                user.delete()
                messages.error(request, "Account created but failed to send verification email. Please contact support.")
                return render("customer_register")
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
        
        if len(phone)!= 10 or not phone.isdigit():
                messages.error(request, "Phone Number must be 10 digits and contain number only")
                return redirect('seller_register')

# Validate password
        errors = password_validation(password)
        if errors:
            messages.error(request, errors[0])
            return redirect('seller_register')
        
        city_obj = city.objects.filter(id=city_id).first() if city_id else None

        user = User.objects.create_user(
            email=email,
            name=name,
            phone=phone,
            city=city_obj,
            password=password,
            user_type='seller',
            is_active=False,
            is_subscribed=False
        )

        if photo:
            user.user_image = photo
            user.save()

        # Send verification email
        mail_subject = 'Verify your email to complete seller registration'
        email_template = 'registration/verification_email.html'
        if send_verification_email(request, user, mail_subject, email_template):
            messages.success(request, "Verification email sent. Please check your email to complete your seller registration.")
            return redirect("seller_register")
        else:
            user.delete()
            messages.error(request, "Failed to send verification email. Please try again..")
            return render("seller_register")
        
    return render(request, "registration/seller_register.html",{'cities':cities})

def seller_register_verify(request):
    lookup_url = "https://dev.khalti.com/api/v2/epayment/lookup/" 
    
    if request.method == 'GET':
        headers = {
            'Authorization': 'key 14e13ca16a514cd1a66f5adc770041fe',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        if not pidx:
            messages.error(request, "Payment Cancled")
            return redirect('seller_payment')

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

        if response.status_code == 200:
        # if new_response['status'] == 'Completed':
            user_id = request.session.get('payment_user_id')
            print(user_id)
            if not user_id:
                messages.error(request, "Session expired. Try again.")
                return redirect('seller_register')
            try:
                user = User.objects.get(id=user_id)

                start_date = datetime.now()
                end_date = start_date + timedelta(days=30)
                    
                user.is_subscribed=True
                user.is_active=True
                user.subscription_end_date=end_date

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
                    amount = int(new_response.get('total_amount')) // 100,
                    transaction_id=transaction_id,
                    payment_date=payment_date,
                    status='success',
                    title='Account Created'
                )
                user.save()
                # Clean up session
                if 'verified_seller' in request.session:
                    del request.session['verified_seller']
                if 'payment_user_id' in request.session:
                    del request.session['payment_user_id']

                messages.success(request, "Payment Successful! Your seller account is now active.")
                return redirect("login")
            except User.DoesNotExist:
                messages.error(request, "User not found. Please register again.")
                return redirect('seller_register')
        else:
            messages.error(request, f"Payment verification failed: {new_response.get('detail', 'Unknown error.')}")
            return redirect('seller_payment')
        
def seller_payment(request):
    if 'verified_seller' not in request.session:
        messages.error(request, "Please complete registration and email verification first.")
        return redirect('seller_registration')
    else:
        user_data = request.session['verified_seller']
        amount = 1000

        if request.method == "POST":
            purchase_order_id = str(uuid.uuid4())  # Generate a unique ID

            url = "https://dev.khalti.com/api/v2/epayment/initiate/"

            payload = json.dumps({
                "return_url": "http://127.0.0.1:8000/accounts/verify_payment",
                "website_url": "http://127.0.0.1:8000/",
                "amount": amount * 100,
                "purchase_order_id": purchase_order_id,
                "purchase_order_name": "Seller Subscription",
                "customer_info": {
                    "name": user_data.get('name'),
                    "email": user_data.get('email'),
                    "phone": user_data.get('phone'),
                }

            })
            headers = {
                'Authorization': 'key 14e13ca16a514cd1a66f5adc770041fe',
                'Content-Type': 'application/json',
            }
            response = requests.post(url, headers=headers, data=payload)
            print(response.text)
            response_data = response.json()

            print("khalti api response:", response_data)
            print(response.status_code)

            if response.status_code == 200:
                request.session['payment_user_id'] = user_data['id']
                return redirect(response_data['payment_url'])
            else:
                messages.error(request, "Payment initialization failed. Please try again.")
                return redirect('seller_payment')

    return render(request, "registration/payment.html", {'amount': amount})

def login_user(request):
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")

            user = authenticate(request, username=email, password=password)

            if user:
                if not user.is_active:
                    messages.error(request, "Activate your account first.")
                    return redirect("login")
                else:
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
            "return_url": "http://127.0.0.1:8000/accounts/verify_renewal",
            "website_url": "http://127.0.0.1:8000/",
            "amount": 500 * 100,   
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "Subscription Renewal",
        })

        headers = {
            'Authorization': 'key 14e13ca16a514cd1a66f5adc770041fe',
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
            'Authorization': 'key 14e13ca16a514cd1a66f5adc770041fe',
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
                amount= 500,
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
    
def send_verification_email(request, user, mail_subject, email_template):
    try:
        current_site = get_current_site(request)
        message = render_to_string(email_template, {
            'user': user,
            'domain': current_site.domain,  # Use domain attribute
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(
            mail_subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def activate(request , uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if user.user_type == "customer":
            user.is_active = True
            user.save()
        elif user.user_type == "seller":
            user.is_active = False
            user.save()

        if user.user_type == 'seller':
            # For sellers, store info in session and redirect to payment
            request.session['verified_seller'] = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'phone': user.phone,
                'city_id': user.city.id if user.city else None,
                'photo': user.user_image.name if user.user_image else None,
                'password': user.password,
            }
            request.session.modified = True
            messages.success(request, 'Email verified! Please complete payment to activate your seller account.')
            return redirect('seller_payment')
        else:
            # For customers, just activate and redirect to login
            messages.success(request, 'Account activated! You can now login.')
            return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        # Check if user exists before checking user_type
        if user is not None and hasattr(user, 'user_type') and user.user_type == 'seller':
            return redirect('seller_register')
        else:
            return redirect('customer_register')