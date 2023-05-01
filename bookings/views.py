from django.shortcuts import render, get_object_or_404, redirect
from bookings.models import Booking, Table
from django.contrib import messages

# Create your views here.


def bookings(request):
    bookings = Booking.objects.filter(user_name=request.user.pk)

    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/bookings.html', context)
