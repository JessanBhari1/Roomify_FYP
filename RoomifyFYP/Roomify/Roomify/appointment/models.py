from django.db import models
from rooms.models import *
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now, timedelta


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
        ('hold', 'Hold'),
        ('cancel', 'Cancel'),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='appointments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_appointments')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='hold')
    created_at = models.DateTimeField(auto_now_add=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    def delete_rejected_appointments(self):
        # Check if the appointment is rejected
        if self.status == 'rejected' and self.rejected_at:
            time_limit = self.rejected_at + timedelta(minutes=10)
            if timezone.now() > time_limit:
                self.delete()

    def __str__(self):
        return f"{self.customer.name} -> {self.seller.name}: {self.date} {self.time}"
    


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    expire_status = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    @staticmethod
    def delete_old_notifications():
        expired_notifications = Notification.objects.filter(expires_at__lt=now())
        if expired_notifications.exists():
            Notification.expire_status = True
            expired_notifications.delete()

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"
    

