from django.contrib import admin
from payment.models import Subscription, Payment

# Register your models here.

admin.site.register(Subscription)
admin.site.register(Payment)
