from django.shortcuts import render, redirect
from accounts.models import *
from core.models import *
from payment.models import *
from rooms.models import *
from django.contrib import messages
from django.utils import timezone
from appointment.models import *
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator



# Create your views here.

# notification handler
def seller_notifications_as_read(request):
    if request.user.is_authenticated:
        # Update notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)  # Mark all as read

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_dashboard'))

def customer_notifications_as_read(request):
    if request.user.is_authenticated:
        # Update notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)  # Mark all as read

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'homepage'))

def homepage(request):
    cities = city.objects.all()
    user = None
    notifications=None
    unread_notifications_count=None
    

    featured_rooms = Room.objects.filter(
        seller__is_subscribed=True
    ).order_by("-id")[:4]



    if request.user.is_authenticated:
        user = request.user
        # Check if the user is not a customer
        if request.user.user_type != 'customer':  
            return redirect('login')
        
        # Delete expired notifications
        Notification.delete_old_notifications()

    
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

            
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()


    data = {
        'user': user,
        'cities': cities,
        'featured_rooms': featured_rooms,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "core/homepage.html", data)

def detail_room(request):
    cities = city.objects.all()
    
    

    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'customer':  
            return redirect('login')
    else:
        return redirect('login')
    
    all_rooms = Room.objects.filter(
        seller__is_subscribed=True
    ).order_by("-id").all()

    city_id = request.GET.get('city')
    if city_id:
        all_rooms = all_rooms.filter(city_id=city_id).all()

    # Initialize variables
    Room_Name = None
    min_price = None
    max_price = None
    searched_location = None

    if request.method == "POST":
        Room_Name = request.POST.get("RoomName")
        min_price = request.POST.get("MinPrice")
        max_price = request.POST.get("MaxPrice")
        searched_location = request.POST.get("SearchLocation")
        print (searched_location)

    # filter by room name
    if Room_Name:
        all_rooms = all_rooms.filter(title__icontains = Room_Name)


    if min_price and max_price:
        all_rooms = all_rooms.filter(rent__gte=min_price, rent__lte=max_price)
    elif min_price:
        all_rooms = all_rooms.filter(rent__gte=min_price)
    elif max_price:
        all_rooms = all_rooms.filter(rent__lte=max_price)

    # filter by city
    if searched_location:
        all_rooms = all_rooms.filter(city=searched_location)

        
    
     # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    paginator = Paginator(all_rooms, 8)  # Show 8 rooms per page

    page_number = request.GET.get("page") 
    all_rooms = paginator.get_page(page_number)


    data={
        'cities':cities,
        'all_rooms': all_rooms,
        'user': user,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }

    return render(request, "core/detail_rooms.html", data)


def single_room_detail(request, slug):
    user = request.user
    room_detail = Room.objects.get(room_slug = slug)
    room_specifications = Room_specification.objects.filter(room=room_detail)
    room_thumbnails = Room_thumbnail.objects.filter(room=room_detail)
    seller = room_detail.seller

    # Delete expired notifications
    Notification.delete_old_notifications()

        
        # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'user': user,
        'room_specifications': room_specifications,
        'room_thumbnails': room_thumbnails,
        'seller': seller,
        'room_detail': room_detail,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "core/single_room_detail.html", data)

def customer_contact(request):
    user = None
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'user': user,
    }
    return render(request, "core/customer_contact.html", data)

def manage_contact(request):
    user=request.user
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        

        contact_obj = contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            type="customer"
        )
        contact_obj.save()
        
        Notification.objects.create(
            user = request.user,
            message=f"{user.name.upper()}: Your Contact Form has been sent Successfully, We will figure out your issue and get back to you soon",
            expires_at=timezone.now() + timedelta(days=30)
        )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

def aboutUs(request):
    notifications = None
    unread_notifications_count = None

    if request.user.is_authenticated:
        user=request.user
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "core/aboutUs.html", data)


# seller dashboard
def seller_dashboard(request):
    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login')
        else:
            user.check_subscription_status()
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()
        

        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()  

        # # for total added rooms of seller in frontend
        seller_total_rooms = Room.objects.filter(seller=user).count()

        appointment_requests = Appointment.objects.filter(seller=user, status='hold')
        total_appointment_requests = appointment_requests.count()

        pending_appointments = Appointment.objects.filter(seller=user, status='pending').order_by('date')
        total_pending_request = pending_appointments.count()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data = {
        'user': user,
        'cities': cities,
        'subscription_remaning_days': subscription_remaning_days,
        'seller_total_rooms': seller_total_rooms,
        'notifications': notifications,
        'unread_notifications_count':unread_notifications_count,
        'total_appointment_requests': total_appointment_requests,
        'total_pending_request': total_pending_request,
    }
    return render(request, "seller/seller_dashboard.html", data)


def seller_rooms(request):
    cities = city.objects.all()

    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        
        # Delete expired notifications
        Notification.delete_old_notifications()

        
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

                # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
        # for fetching seller room object in frontend
        seller_rooms_table = Room.objects.filter(seller=user).order_by("-id")

    data = {
        'cities': cities,
        'seller_rooms_table': seller_rooms_table,
        'user': user,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "seller/seller_rooms.html", data)

def room_add(request):
    cities = city.objects.all()  # Assuming you have a City model   
    user=request.user    
    # Delete expired notifications
    Notification.delete_old_notifications()

        
    # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    if request.method == 'POST':
        room_title = request.POST.get('name')
        room_description = request.POST.get('description')
        city_id = request.POST.get('city')
        rent = request.POST.get('rent')
        room_image = request.FILES.get('room_image')
        room_slug = room_title.replace(" ", "-").lower()

        city_obj = city.objects.filter(id = city_id).first()

        # creating room
        room = Room.objects.create(
            seller = request.user,
            title = room_title,
            description = room_description,
            rent = rent,
            room_img = room_image,
            city = city_obj,
            room_slug = room_slug
        )

        # Handle multiple room images (thumbnails)
        thumbnails = []
        for i in range(1, 11):  # Adjust range if more thumbnails are expected
            thumbnail = request.FILES.get(f'room_image_{i}')
            if thumbnail:
                thumbnails.append(thumbnail)

        for thumbnail in thumbnails:
            Room_thumbnail.objects.create(room=room, thumbnail_img=thumbnail)


        # Handle room specifications
        spec_names = request.POST.getlist('spec_name[]')
        spec_details = request.POST.getlist('spec_detail[]')

        for name, detail in zip(spec_names, spec_details):
            Room_specification.objects.create(room=room, spec_name=name, spec_detail=detail)
        return redirect('seller_dashboard') 

    data = {
        'cities': cities,
        'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "seller/room_add.html", data)


def update_room(request, room_id):
    cities = city.objects.all()

    # Delete expired notifications
    Notification.delete_old_notifications()

    user = request.user
    seller_rooms = Room.objects.filter(seller=user)

    room_to_update = Room.objects.get(id=room_id, seller=user)

    # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

    # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    if request.method == 'POST':
        # update room fields
        room_to_update.title = request.POST.get("name", room_to_update.title)
        room_to_update.rent = request.POST.get("rent", room_to_update.rent)
        room_to_update.description = request.POST.get("description", room_to_update.description)

        # Update city only if a new city is selected
        selected_city_id = request.POST.get("city")
        if selected_city_id and selected_city_id.isdigit():  # Check if a valid city ID is provided
            try:
                selected_city = city.objects.get(id=int(selected_city_id))
                room_to_update.city = selected_city
            except city.DoesNotExist:
                # If the selected city does not exist, keep the previous city
                messages.warning(request, "Selected city does not exist. Keeping the previous city.")
        # If no city is selected, keep the previous city (no action needed)

        
        # Update main image 
        if "room_image" in request.FILES:
            room_to_update.room_img = request.FILES["room_image"]
            # room_to_update.room_img = request.FILES.get("room_image", room_to_update.room_img)
        room_to_update.save()


        # Update main image
        if "room_image" in request.FILES:
            room_to_update.room_img = request.FILES["room_image"]

        room_to_update.save()

        # Update or Replace Thumbnails
        for i, thumbnail_obj in enumerate(room_to_update.thumbnails.all(), start=1):
            new_thumbnail = request.FILES.get(f'room_image_{i}')
            if new_thumbnail:
                # If a new thumbnail is uploaded, replace the existing one
                thumbnail_obj.thumbnail_img = new_thumbnail
                thumbnail_obj.save()

        # Add New Thumbnails
        for i in range(len(room_to_update.thumbnails.all()) + 1, 11):  # Adjust range if more thumbnails are expected
            new_thumbnail = request.FILES.get(f'room_image_{i}')
            if new_thumbnail:
                Room_thumbnail.objects.create(room=room_to_update, thumbnail_img=new_thumbnail)

        # Update Existing Specifications
        old_spec_names = request.POST.getlist("old_spec_name[]")
        old_spec_details = request.POST.getlist("old_spec_detail[]")

        existing_specs = Room_specification.objects.filter(room=room_to_update)

        for spec_obj, new_name, new_detail in zip(existing_specs, old_spec_names, old_spec_details):
            if new_name.strip() and new_detail.strip():  # Ensure non-empty values
                spec_obj.spec_name = new_name
                spec_obj.spec_detail = new_detail
                spec_obj.save()

        # Add New Specifications
        new_spec_names = request.POST.getlist("new_spec_name[]")
        new_spec_details = request.POST.getlist("new_spec_detail[]")

        for name, detail in zip(new_spec_names, new_spec_details):
            if name.strip() and detail.strip():  # Avoid creating empty specifications
                Room_specification.objects.create(room=room_to_update, spec_name=name, spec_detail=detail)
        messages.success(request, "Room Updated Successfully")
        return redirect('seller_rooms')


    
    data={
        'seller_rooms': seller_rooms,
        'cities': cities,
        'room_to_update': room_to_update, 
        'user': user,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,


    }
    return render(request, "seller/update_room.html", data)



def seller_appointments(request):
    user = request.user

    # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')
    print(notifications)

    # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

            # Delete rejected notification
    appointments = Appointment.objects.filter(seller=user, status='rejected')
    for appointment in appointments:
            appointment.delete_rejected_appointments()  


    appointment_requests = Appointment.objects.filter(seller=user, status='hold')
    total_appointment_requests = appointment_requests.count()

    pending_appointments = Appointment.objects.filter(seller=user, status='pending').order_by('date')
    total_pending_request = pending_appointments.count()

    appointment_completed = Appointment.objects.filter(seller=user, status='done')
    total_appointment_completed = appointment_completed.count()

    appointment_canceled = Appointment.objects.filter(seller=user, status='cancel')
    total_appointment_canceled = appointment_canceled.count()




    # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'user':user,
        'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
        'total_pending_request': total_pending_request,
        'total_appointment_requests': total_appointment_requests,
        'total_appointment_completed': total_appointment_completed,
        'total_appointment_canceled': total_appointment_canceled,
    }
    return render(request, "seller/appointment/seller_appointments.html", data)

def appointment_request(request):
    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login')
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()

        
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments() 

        # # Fetch appointment requests for the seller
        appointment_requests = Appointment.objects.filter(seller=user, status='hold').order_by('date')

        data={
            'appointment_requests': appointment_requests,
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,

        }

            
    return render(request, "seller/appointment/appointment_request.html", data)

def appointment_pending(request):
    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login')
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()

        pending_appointments = Appointment.objects.filter(seller=user, status='pending').order_by('date')

        data={
            'pending_appointments': pending_appointments,
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        }

    return render(request, "seller/appointment/appointment_pending.html", data)


def appointment_completed(request):

    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login')
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()

                # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()

        completed_appointments = Appointment.objects.filter(seller=user, status='done').order_by('date')

        data={
            'completed_appointments': completed_appointments,
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
            
        }

    return render(request, "seller/appointment/appointment_completed.html", data)

def appointment_cancel(request):
    
    subscription_remaning_days = None
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login')
        
        # calculate seller subscription remaning days
        if user.is_subscribed and user.subscription_end_date:
            now = timezone.now()
            subscription_remaning_days = (user.subscription_end_date - now).days
            if subscription_remaning_days < 0:
                subscription_remaning_days = 0

        # Delete expired notifications
        Notification.delete_old_notifications()

        
        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()
        
        # Delete rejected notification
        appointments = Appointment.objects.filter(seller=user, status='rejected')
        for appointment in appointments:
            appointment.delete_rejected_appointments()

        canceled_appointments = Appointment.objects.filter(seller=user, status='cancel').order_by('date')

        data={
            'canceled_appointments': canceled_appointments,
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        }
    return render(request, "seller/appointment/appointment_cancel.html", data)

# seller subscription management 
def subscription_management(request):
    subscriptions = Subscription.objects.filter(seller=request.user).order_by("-id")[:1]
    payments = Payment.objects.filter(seller=request.user).order_by("-id")

    data={
        'subscriptions': subscriptions,
        'payments': payments,
    }
    return render(request, "seller/subscription/subscription_manage.html", data)

def seller_profile(request):
    cities = city.objects.all()
    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'seller':
            return redirect('login_user')
        else:
            user.check_subscription_status()
        # Delete expired notifications
        Notification.delete_old_notifications()

        # Fetch notifications for the seller
        notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        # Count unread notifications
        unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    else:
        messages.error(request, "Unauthorized User")
        return redirect('login_user')

    data={
        'cities':cities,
        'notifications':notifications,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, "seller/seller_profile.html", data)

def seller_profile_update(request):
    if request.method == 'POST':
        seller_name = request.POST.get("name")
        seller_email = request.POST.get("email")
        seller_password = request.POST.get("password")
        seller_phone = request.POST.get("phone")
        seller_city = request.POST.get("city")
        seller_img = request.FILES.get("profile_image")
        seller_id = request.user.id
        print(seller_img)

        seller = User.objects.get(id=seller_id)

            
        # Check if the email already exists
        if seller_email and seller_email != seller.email and User.objects.filter(email=seller_email).exclude(id=seller_id).exists(): 
        #exclude checks for duplicate email in databse exclude remove the user and checks other user 
            messages.error(request, "Email already exists!")
            return redirect("seller_profile")
        

        # Check if phone is changed and already used by another user
        if seller_phone and seller_phone != seller.phone and User.objects.filter(phone=seller_phone).exclude(id=seller_id).exists():
            messages.error(request, "This phone number is already in use by another account.")
            return redirect('seller_profile')

        # fetch the user
        seller.name = seller_name
        seller.email = seller_email
        seller.phone = seller_phone

        # Update city only if a new city is provided
        if seller_city:
            try:
                seller.city = city.objects.get(city=seller_city)
            except city.DoesNotExist:
                messages.error(request, "Invalid City Selected")
                return redirect("seller_profile")

        # Update profile image if provided
        if seller_img:
            seller.user_image = seller_img
        
        # Update password only if provided
        if seller_password:
            seller.set_password(seller_password)
            seller.save()
            messages.success(request, "Profile Updated Succesfully please login again")
            return redirect("login")

        
        seller.save()
        messages.success(request, "Profile Updated Succesfully")
        return redirect("seller_profile")
    
    return render (request, "seller/seller_profile.html")