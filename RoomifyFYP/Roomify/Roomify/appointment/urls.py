from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from appointment import views


urlpatterns = [
    path('customer_appointment_request/<int:room_id>', views.customer_appointment_request, name="customer_appointment_request"),
    path('appointment_request_accept/<int:appointment_id>/', views.appointment_request_accept, name='appointment_request_accept'),
    path('appointment_request_reject/<int:appointment_id>/', views.appointment_request_reject, name='appointment_request_reject'),
    path('appointment_request_done/<int:appointment_id>/', views.appointment_request_done, name='appointment_request_done'),
    path('appointment_request_cancel/<int:appointment_id>/', views.appointment_request_cancel, name='appointment_request_cancel'),


]