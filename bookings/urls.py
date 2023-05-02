from django.urls import path
from . import views

urlpatterns = [
    path('bookings/', views.bookings, name='bookings'),
    path('bookings/edit/<int:booking_id>/',
         views.edit_booking, name='edit_booking'),
]
