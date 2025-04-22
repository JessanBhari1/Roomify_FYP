from django.urls import path
from . import views

urlpatterns = [
    
    path('customer/chats/', views.customer_chat_list, name='customer_chat_list'),
    path('seller/chats/', views.seller_chat_list, name='seller_chat_list'),
    path('chat/<slug:room_slug>/', views.initiate_chat, name='initiate_chat'),
    path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),

    # path('chat/delete/<int:room_id>/', views.delete_chat_room, name='delete_chat_room'),


]