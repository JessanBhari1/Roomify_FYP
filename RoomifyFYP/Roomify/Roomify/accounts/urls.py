from django.urls import path
from accounts import views


urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('customer_register/', views.customer_register, name='customer_register'),
    path('seller_register/', views.seller_register, name='seller_register'),
    path("verify_payment/", views.seller_register_verify, name="verify_payment"),
    path("register_option/", views.register_option, name="register_option"),
    path("Subscription_renew/", views.Subscription_renew, name="Subscription_renew"),
    path('verify_renewal/', views.verify_renewal, name='verify_renewal'),


]