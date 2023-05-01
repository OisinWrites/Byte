from django.shortcuts import render, redirect
from django.utils.timezone import timedelta
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models

from .forms import BookingForm
from .models import Booking, Table


def bookings(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            user_email = models.ForeignKey(get_user_model(),
                                           on_delete=models.CASCADE)
            user_name = models.ForeignKey(get_user_model(),
                                          on_delete=models.CASCADE)
            booking.user_email = request.user
            booking.user_name = request.user
            start_time = form.cleaned_data['start_time']
            end_time = start_time + timedelta(minutes=105)
            size_of_party = form.cleaned_data['size_of_party']
            tables = Table.objects.filter(size=size_of_party,
                                          is_available=True)
            for table in tables:
                bookings = Booking.objects.filter(
                    table=table,
                    start_time__gte=start_time-timedelta(minutes=105),
                    end_time__lte=end_time
                )
                if not bookings:
                    booking.table = table
                    booking.end_time = end_time
                    booking.save()
                    table.is_available = False
                    table.save()
                    return redirect('bookings', pk=booking.pk)
            messages.error(request, 'No table is available for the requested'
                                    ' time and party size.'
                                    ' Please select a new time.')
            messages.success(request, 'Your booking has been made.')
            return redirect('bookings')
        else:
            messages.error(request, 'There was an error with your booking.')
    else:
        form = BookingForm()
    context = {'form': form}
    return render(request, 'bookings/bookings.html', context)
