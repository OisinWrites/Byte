from django.shortcuts import render
from bookings.models import Booking, Table

# Create your views here.


def bookings(request):
    bookings = Booking.objects.filter(user_email=request.user.email)

    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/bookings.html', context)
