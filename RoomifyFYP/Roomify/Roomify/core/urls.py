from django.urls import path
from core import views


urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('detail_room/', views.detail_room, name="detail_room"),
    path('single_room_detail/<slug>', views.single_room_detail, name="single_room_detail"),


    path('seller_dashboard/', views.seller_dashboard, name="seller_dashboard"),
    path('seller_rooms/', views.seller_rooms, name="seller_rooms"),
    path('room_add/', views.room_add, name="room_add"),
    path("updateroom/<int:room_id>", views.update_room, name="update_room"),

    # appointment
    path('seller_appointments/', views.seller_appointments, name="seller_appointments"),
    path('appointment_request/', views.appointment_request, name="appointment_request"),
    path('appointment_pending/', views.appointment_pending, name="appointment_pending"),
    path('appointment_completed/', views.appointment_completed, name="appointment_completed"),
    path('appointment_cancel/', views.appointment_cancel, name="appointment_cancel"),

    # notification
    path('seller_notifications_as_read/', views.seller_notifications_as_read, name="seller_notifications_as_read"),
    path('customer_notifications_as_read/', views.customer_notifications_as_read, name="customer_notifications_as_read"),



]