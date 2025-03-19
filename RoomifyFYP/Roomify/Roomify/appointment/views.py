from django.shortcuts import render, redirect
from .models import Appointment, Notification
from rooms.models import Room
from django.utils.timezone import now, timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib import messages


# customer send appointment
def customer_appointment_request(request, room_id):
    if request.method == 'POST':
        room = Room.objects.get(id=room_id)
        seller = room.seller
        date = request.POST.get('date')
        time = request.POST.get('time')

        # Delete expired notifications
        Notification.delete_old_notifications()

        # Creating a new appointment request
        appointment = Appointment.objects.create(
            room=room,
            customer=request.user,
            seller=seller,
            date=date,
            time=time,
            status='hold'
        )

        Notification.objects.create(
            user=seller,
            message=f"New appointment request for {room.title} from {request.user.name}.",
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        return redirect('single_room_detail', slug=room.room_slug)
    




# seller appointment approval
def appointment_request_accept(request, appointment_id):        
    if request.method == "POST":
        appointment = Appointment.objects.get(id=appointment_id)

        # ensuring only the seller can approve
        if appointment.seller == request.user:
            appointment.status = 'pending'
            appointment.save()

            # create notification to the customer 
            Notification.objects.create(
                user = appointment.customer,
                message=f"Your appointment request for {appointment.room.title} has been approved by {appointment.seller.name}.",
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

# seller appointment reject
def appointment_request_reject(request, appointment_id):
    if request.method == "POST":
        appointment = Appointment.objects.get(id=appointment_id)

        if appointment.seller == request.user:
            appointment.status = 'rejected'
            appointment.rejected_at = timezone.now()
            appointment.save()

            Notification.objects.create(
                user = appointment.customer,
                message=f"Your appointment request for {appointment.room.title} has been rejected by {appointment.seller.name}, for further inquiry contact seller {appointment.seller.phone}.",
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_appointments'))
        
        else:
            messages.error(request, "You're not authorized to reject this appointment")
            return redirect("login")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




# seller appointment Finished
def appointment_request_done(request, appointment_id):
    if request.method == "POST":
        appointment = Appointment.objects.get(id=appointment_id)

        if appointment.seller == request.user:
            appointment.status = 'done'
            appointment.save()

            Notification.objects.create(
                user = appointment.customer,
                message=f"Your appointment with {appointment.seller.name} for {appointment.room.title} has been Finished.",
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_appointments'))
        
        else:
            messages.error(request, "You're not authorized to reject this appointment")
            return redirect("login")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_appointments'))


# seller appointment Cancel
def appointment_request_cancel(request, appointment_id):
    if request.method == "POST":
        appointment = Appointment.objects.get(id=appointment_id)

        if appointment.seller == request.user:
            appointment.status = 'cancel'
            appointment.save()

            Notification.objects.create(
                user = appointment.customer,
                message=f"Your appointment with {appointment.seller.name} for {appointment.room.title} has been Cancel.",
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_appointments'))
        
        else:
            messages.error(request, "You're not authorized to reject this appointment")
            return redirect("login")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'seller_appointments'))

