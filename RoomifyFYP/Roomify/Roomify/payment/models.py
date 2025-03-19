from django.db import models
from accounts.models import User

# Create your models here.
class Subscription(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    transaction_id = models.CharField(max_length=100)  # Khalti transaction ID
    start_date = models.DateTimeField(auto_now_add=True)  
    end_date = models.DateTimeField() 
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.seller.email
    


class Payment(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Payment amount in NPR
    transaction_id = models.CharField(max_length=100)  # Khalti transaction ID
    payment_date = models.DateTimeField(auto_now_add=True)  # Payment date
    status = models.CharField(max_length=20, default='pending')  # Payment status: pending, success, failed

    def __str__(self):
        return f"{self.seller.email} - {self.amount}"
