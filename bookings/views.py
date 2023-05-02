from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseBadRequest

from datetime import timedelta

from .forms import BookingForm
from .models import Booking, Table, TableAvailability


def bookings(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user_email = request.user
            booking.user_name = request.user
            start_time = form.cleaned_data['start_time']
            if start_time < timezone.now():
                form.add_error('start_time',
                               "Whoops! You're already late"
                               " for dinner. "
                               "Choose a day that hasn't happened yet."
                               )
            end_time = start_time + timedelta(minutes=105)
            size_of_party = form.cleaned_data['size_of_party']
            tables = Table.objects.filter(size__gte=size_of_party) \
                .order_by('size')
            for table in tables:
                table_availabilities = TableAvailability.objects.filter(
                    table=table,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                if not table_availabilities:
                    booking.table = table
                    booking.end_time = end_time
                    booking.save()
                    table_availability = TableAvailability(
                        table=table,
                        start_time=start_time,
                        end_time=end_time
                    )
                    table_availability.save()
                    messages.success(request, 'Your booking has been made.')
                    return redirect('bookings')
            messages.error(request, 'No table is available for the requested'
                                    ' time and party size.'
                                    ' Please select a new time.')
        else:
            messages.error(request, 'There was an error with your booking.')
    else:
        form = BookingForm()
    current_bookings = Booking.objects.filter(
        start_time__gte=timezone.now(),
        user_email=request.user
    ).order_by('start_time')
    context = {'form': form, 'current_bookings': current_bookings}
    return render(request, 'bookings/bookings.html', context)


def update_table_availability():
    now = datetime.now()
    tables = Table.objects.all()
    for table in tables:
        bookings = Booking.objects.filter(table=table, end_time__gte=now)
        if bookings:
            table.is_available = False
        else:
            table.is_available = True
        table.save()
