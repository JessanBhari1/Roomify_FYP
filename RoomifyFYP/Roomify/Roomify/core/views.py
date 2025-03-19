from django.shortcuts import render, redirect
from accounts.models import *
from core.models import *
from payment.models import *
from rooms.models import *
from django.contrib import messages
from django.utils import timezone
from appointment.models import *
from django.http import HttpResponseRedirect



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
    

    featured_rooms = Room.objects.all().order_by("-id")[:4]



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
    all_rooms = Room.objects.all().order_by("-id")[:8]
    print(all_rooms)

    if request.user.is_authenticated:
        user = request.user
        if request.user.user_type != 'customer':  
            return redirect('login')
    else:
        return redirect('login')
    
        # Fetch notifications for the seller
    notifications = Notification.objects.filter(user=user, expire_status=False).order_by('-created_at')

        
        # Count unread notifications
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False, expire_status=False).count()

    data={
        'user': user,
        'all_rooms': all_rooms,
        'cities': cities,
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


# seller dashboard
def seller_dashboard(request):
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