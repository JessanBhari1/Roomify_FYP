
from django.contrib import admin
from .models import *

# Register your models here.
class RoomSpec_Inline(admin.TabularInline):
    model = Room_specification
    extra = 1  # Allows adding more specs dynamically

class Room_thumb(admin.TabularInline):
    model = Room_thumbnail
    extra = 1  # Allows adding more thumbnails dynamically


# Custom admin for Room model
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller')
    search_fields = ('title', 'seller')
    list_filter = ('seller',)
    ordering = ('title',)

    inlines = (RoomSpec_Inline, Room_thumb)

admin.site.register(Room, RoomAdmin)
