from django.shortcuts import render, get_object_or_404, redirect
from bookings.models import Booking, Table
from django.contrib import messages
from bookings.forms import BookingForm


def bookings(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user_email = request.user.email
            booking.save()
            messages.success(request, 'Your booking has been made.')
            return redirect('bookings')
        else:
            messages.error(request, 'There was an error with your booking.')
    else:
        form = BookingForm()
    context = {'form': form}
    return render(request, 'bookings/bookings.html', context)
