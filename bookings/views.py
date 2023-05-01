from django.shortcuts import render, get_object_or_404, redirect
from bookings.models import Booking, Table
from django.contrib import messages
from .forms import BookingForm


def bookings(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user_email = request.user.email
            booking.save()
    else:
        form = BookingForm()
    return render(request, 'bookings/bookings.html', {'form': form})
