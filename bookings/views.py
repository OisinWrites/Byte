from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.db.models import Q

from datetime import timedelta

from .forms import BookingForm
from .models import Booking, Table, TableAvailability


def bookings(request, booking_id=None):
    successful_bookings = []

    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request, request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
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
                    successful_bookings.append(booking)
                    messages.success(request, 'Your booking has been made.')
                    return redirect('bookings')
            form.add_error('size_of_party', 'No table is available'
                           ' for the requested'
                           ' time and party size.'
                           ' Please select a new time.')
        else:
            form.add_error(None, 'There was an error with your booking.')
    else:
        form = BookingForm(request, instance=booking)

    current_bookings = Booking.objects.filter(
        Q(start_time__gte=timezone.now()) | Q(
            user_id=request.user.id)).order_by('start_time')

    context = {
        'form': form,
        'current_bookings': current_bookings,
        'successful_bookings': successful_bookings,
        'edit_booking': booking,
        # pass the booking to the template if it exists
    }
    return render(request, 'bookings/bookings.html', context)


def edit_booking(request, booking_id):
    successful_bookings = []

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.user != request.user:
        raise Http404("Booking not found")

    if request.method == 'POST':
        form = BookingForm(request, request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
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
                    successful_bookings.append(booking)
                    messages.success(request, 'Your booking has been updated.')
                    return redirect('bookings')
            form.add_error('size_of_party', 'No table is available'
                           ' for the requested'
                           ' time and party size.'
                           ' Please select a new time.')
        else:
            form.add_error(None, 'There was an error with your booking.')
    else:
        form = BookingForm(request, instance=booking)

    current_bookings = Booking.objects.filter(
        Q(start_time__gte=timezone.now()) | Q(
            user_id=request.user.id)).order_by('start_time')

    context = {
        'form': form,
        'current_bookings': current_bookings,
        'successful_bookings': successful_bookings,
        'edit_booking': booking,
        # pass the booking to the template if it exists
    }
    return render(request, 'bookings/edit_booking.html', context)


def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    table_availability = TableAvailability.objects.filter(
        table=booking.table,
        start_time=booking.start_time,
        end_time=booking.end_time
    ).delete()
    booking.delete()
    messages.success(request, 'Your booking has been deleted.')
    return redirect('bookings')
