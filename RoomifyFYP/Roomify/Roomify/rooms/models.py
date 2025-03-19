from django.db import models
from accounts.models import *
from autoslug import AutoSlugField


# Create your models here.
class Room(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Seller_rooms')
    title = models.CharField(max_length=100)
    description = models.TextField()
    city = models.ForeignKey(city, on_delete=models.CASCADE, related_name='room_city')
    rent = models.IntegerField()
    room_img = models.ImageField(upload_to='img/room_img', default='')
    created_at = models.DateTimeField(auto_now_add=True)
    room_slug = AutoSlugField(populate_from='name', unique=True, null=True, default=None)

    def __str__(self):
        return self.title
    
class Room_specification(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="specifications")
    spec_name = models.CharField(max_length=50)
    spec_detail = models.CharField(max_length=200)

class Room_thumbnail(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="thumbnails")
    thumbnail_img = models.ImageField(upload_to="img/room_img", default="", null=True)