from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import remove_favorite
from .views import resend_pin  

urlpatterns = [

    # User registration and login paths
    path('verify_pin/', views.verify_pin, name='verify_pin'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('signup/', views.sign_up, name='signup'),
    # Car-related views
    path('', views.car_list, name='car_list'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('upload/', views.upload_car, name='upload_car'),
    path('my_cars/', views.my_cars, name='my_cars'),
    path('add_favorite/<int:car_id>/', views.add_favorite, name='add_favorite'),
    path('favorites/remove/<int:car_id>/', remove_favorite, name='remove_favorite'),
    path('remove_car/<int:car_id>/', views.remove_car, name='remove_car'),
    # Favorites and recommended cars views
    path('favorites/', views.favorite_cars, name='favorites'),
    path('recommended/', views.recommend_cars_view, name='recommended_cars'),
    # Account-related views
    path('account/', views.account_details, name='account_details'),
    path('preferences/', views.update_preferences, name='update_preferences'),
    path('reset_preferences/', views.reset_preferences, name='reset_preferences'),

    # Password reset URLs with custom templates
    path('password_reset/', 
    auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
    name='password_reset'),

    path('password_reset/done/', 
    auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
    name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
    auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
    name='password_reset_confirm'),

    path('reset/done/', 
    auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
    name='password_reset_complete'),

    path('resend_pin/', resend_pin, name='resend_pin'),
    ]