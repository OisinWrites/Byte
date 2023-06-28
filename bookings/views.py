from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseBadRequest, HttpResponse
from django.http import JsonResponse
from django.db.models import Q, Count, F, Sum
from django.urls import reverse
from django.utils.timezone import make_aware
from django.db.models.functions import Trunc


from datetime import datetime, time, timedelta

from .forms import BookingForm, TableForm
from .models import Booking, Table, TableAvailability


def diary(request):
    def next_day(date):
        """Returns the next day from a given date."""
        next_day = date + timedelta(days=1)
        return make_aware(datetime(next_day.year,
                          next_day.month, next_day.day, 0, 0, 0))

    tables = Table.objects.all().order_by('number')

    """Set the date range for filter"""
    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    next_week = today + timedelta(days=7)

    """Filter bookings by not earlier than the current day"""
    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    bookings = Booking.objects.filter(start_time__gte=today)

    """Get search query from request"""
    search_query = request.GET.get('search', '')

    """Get filter query from request"""
    filter_query = request.GET.get('filter', '')

    """Filter bookings by user name if search query is provided"""
    if search_query:
        bookings = bookings.filter(user__username__icontains=search_query)

    """Filter bookings by day or week if filter query is provided"""
    if filter_query == 'day':
        start_date = today
        end_date = start_date + timedelta(days=1)
        bookings = bookings.filter(
            start_time__range=(start_date, end_date)).order_by('start_time')
    elif filter_query == 'week':
        start_date = today
        end_date = start_date + timedelta(days=7)
        bookings = bookings.filter(
            start_time__range=(start_date, end_date)).order_by('start_time')

    """
    Annotate the query set
    with a truncated start_time field
    (day-level precision)
    """
    bookings = bookings.annotate(day=Trunc('start_time', 'day'))

    """Perform grouping by day and count the number of bookings per day"""
    grouped_results = bookings.values('day').annotate(count=Count('id'))

    for result in grouped_results:
        result['bookings'] = bookings.filter(start_time__date=result['day'])
        result['total_covers'] = result['bookings'].aggregate(
            total_covers=Sum('size_of_party'))['total_covers']

    context = {
        'grouped_results': grouped_results,
        'filter_query': filter_query,
        'search_query': search_query,
    }

    return render(request, 'bookings/the_diary.html', context)


def bookings(request, booking_id=None):
    """Initialise empty list for bookings to populate later"""
    successful_bookings = []

    """Initialises the booking variable to none, looks for new id"""
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)

    all_bookings = Booking.objects.filter(
        user_id=request.user.id).order_by('start_time')

    users_bookings = Booking.objects.filter(user=request.user)

    """Code triggeered by form submission.
        Saves instance of the form as the booking variable,
        takes in the current user."""
    if request.method == 'POST':
        form = BookingForm(request, request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            """Validate start time and add error if fails"""
            start_time = form.cleaned_data['start_time']
            if start_time < timezone.now():
                messages.error(request,
                               "Whoops! You're already late"
                               " for dinner."
                               "Choose a day that hasn't happened yet."
                               )
            else:
                """Generates end time from start time for use by availabilities
                    model to create a time slot"""
                end_time = start_time + timedelta(minutes=105)
                size_of_party = form.cleaned_data['size_of_party']
                """Order tables by size so that the smallest suitable
                    table possible is selected first"""
                tables = Table.objects.filter(size__gte=size_of_party) \
                    .order_by('size')
                """Checks if booking request clashes
                    with existing booking slot"""
                for table in tables:
                    table_availabilities = TableAvailability.objects.filter(
                        table=table,
                        start_time__lt=end_time,
                        end_time__gt=start_time,
                    )
                    """If not then saves the bookings and
                        creates and saved a slot"""
                    if not table_availabilities:
                        booking.table = table
                        booking.end_time = end_time
                        booking.save()
                        successful_bookings.append(booking)
                        booking_instance = Booking.objects.get(id=booking.id)
                        table_availability = TableAvailability(
                            table=table,
                            start_time=start_time,
                            end_time=end_time,
                            booking_id=booking
                        )
                        table_availability.save()
                        messages.success(
                            request, 'Your booking has been made.')
                        return redirect('edit_booking', booking_id=booking.id)
                        """Else error handling"""
                messages.error(request, 'No table is available'
                               ' for the requested'
                               ' time and party size.'
                               ' Please select a new time.')
        else:
            """Error handling if form invalid"""
            messages.error(request, 'There was an error with your booking.')
    else:
        """Where no id is found form returns to initial state"""
        form = BookingForm(request, instance=booking)

    """Creates list of bookings not older than current date for
        logged in user"""
    current_bookings = Booking.objects.filter(
        Q(start_time__gte=timezone.now()) | Q(
            user_id=request.user.id)).order_by('start_time')

    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    bookings = Booking.objects.filter(user=request.user, start_time__gte=today)

    bookings = bookings.annotate(day=Trunc('start_time', 'day'))

    grouped_results = bookings.values('day').annotate(count=Count('id'))

    for result in grouped_results:
        result['bookings'] = bookings.filter(start_time__date=result['day'])

    """Context list to call on these variables from the template"""
    context = {
        'booking': booking,
        'all_bookings': all_bookings,
        'users_bookings': users_bookings,
        'grouped_results': grouped_results,
        'form': form,
        'current_bookings': current_bookings,
        'successful_bookings': successful_bookings,
        'edit_booking': booking,
    }
    return render(request, 'bookings/bookings.html', context)


@login_required
def my_bookings(request, booking_id=None):
    """Initialise empty list for bookings to populate later"""
    successful_bookings = []

    """Initialises the booking variable to none, looks for new id"""
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    all_bookings = Booking.objects.filter(
        user=request.user).order_by('start_time')

    users_bookings = all_bookings

    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    bookings = Booking.objects.filter(user=request.user, start_time__gte=today)

    """Creates list of bookings not older than current date for
        logged in user"""
    current_bookings = bookings.order_by('start_time')

    """
    Annotate the query set
    with a truncated start_time field
    (day-level precision)
    """
    bookings = bookings.annotate(day=Trunc('start_time', 'day'))

    """Perform grouping by day and count the number of bookings per day"""
    grouped_results = bookings.values('day').annotate(count=Count('id'))

    for result in grouped_results:
        result['bookings'] = bookings.filter(start_time__date=result['day'])

    """Context list to call on these variables from the template"""
    context = {
        'booking': booking,
        'grouped_results': grouped_results,
        'all_bookings': all_bookings,
        'users_bookings': users_bookings,
        'current_bookings': current_bookings,
        'successful_bookings': successful_bookings,
        'edit_booking': booking,
        # pass the booking to the template if it exists
    }
    return render(request, 'bookings/user_bookings.html', context)


def edit_booking(request, booking_id):
    successful_bookings = []
    booking = get_object_or_404(Booking, id=booking_id)
    all_bookings = Booking.objects.filter(
        user_id=request.user.id).order_by('start_time')
    users_bookings = Booking.objects.filter(user=request.user)

    if booking.user != request.user and not request.user.is_superuser:
        messages.error(
            request, "You may not access another user's booking information")
        return redirect('home')

    if request.method == 'POST':
        form = BookingForm(request, request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            start_time = form.cleaned_data['start_time']
            if start_time < timezone.now():
                messages.error(
                    request, "Whoops! You're already late for dinner. "
                             "Choose a day that hasn't happened yet.")
            else:
                end_time = start_time + timedelta(minutes=105)
                size_of_party = form.cleaned_data['size_of_party']
                tables = Table.objects.filter(
                    size__gte=size_of_party).order_by('size')
                for table in tables:
                    table_availabilities = TableAvailability.objects.filter(
                        table=table,
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    )
                    if not table_availabilities:
                        TableAvailability.objects.filter(
                            id_of_booking=booking.id).delete()

                        booking.end_time = start_time + timedelta(minutes=105)
                        booking.table = table
                        booking.start_time = start_time
                        booking.save()

                        table_availability = TableAvailability(
                            table=table,
                            start_time=start_time,
                            end_time=booking.end_time,
                            booking_id=booking,
                        )
                        table_availability.save()

                        successful_bookings.append(booking)

                if successful_bookings:
                    messages.success(request, 'Your booking has been updated.')

                    if 'return_to_bookings' in request.POST:
                        return redirect('bookings')
                    elif 'return_to_my_bookings' in request.POST:
                        return redirect('my_bookings')
                else:
                    messages.error(request, 'No table is available for the '
                                   'requested time and party size. '
                                   'Please select a new time.')
        else:
            messages.error(request, 'There was an error with your booking.')
    else:
        form = BookingForm(request, instance=booking)

        """Creates list of bookings not older than current date for
        logged in user"""
    current_bookings = Booking.objects.filter(
        Q(start_time__gte=timezone.now()) | Q(
            user_id=request.user.id)).order_by('start_time')

    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    bookings = Booking.objects.filter(user=request.user, start_time__gte=today)

    bookings = bookings.annotate(day=Trunc('start_time', 'day'))

    grouped_results = bookings.values('day').annotate(count=Count('id'))

    for result in grouped_results:
        result['bookings'] = bookings.filter(start_time__date=result['day'])

    context = {
        'booking': booking,
        'all_bookings': all_bookings,
        'users_bookings': users_bookings,
        'grouped_results': grouped_results,
        'form': form,
        'current_bookings': current_bookings,
        'successful_bookings': successful_bookings,
        'edit_booking': booking,
    }

    return render(request, 'bookings/edit_booking.html', context)


def delete_booking(request, booking_id):
    """Identify object by id"""
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the user is the booking user or a superuser
    if booking.user == request.user or request.user.is_superuser:
        """Finds and deletes by detail match"""
        table_availability = TableAvailability.objects.filter(
            table=booking.table,
            start_time=booking.start_time,
            end_time=booking.end_time
        ).delete()
        booking.delete()
        """Returns success and reverses url, as the current url is no longer
        valid as the booking object id was populating the end of the url"""
        messages.success(request, 'Your booking has been deleted.')
        return redirect(reverse('bookings'))
    else:
        # If the user is neither the booking user nor a superuser,
        # handle the unauthorised access
        messages.error(
            request, 'You are not authorised to delete this booking.')
        return redirect(reverse('home'))


"""This is a convoluted view that essentially melds two purposes
    so as to confine the admin CRUD abilities to a single html file.
    This view iterates the existing bookings, through search and
    filter methods. It allows the admin to view, create, and delete tables
    for the restaurant, but not edit them as quick deletion and recreation
    was deemed sufficient for this particularly simple model."""


def save_table_location(request):
    if request.method == 'POST':
        print("Hi Oisín")
        table_id = request.POST.get('table_id')
        left = request.POST.get('left')  # Retrieve left value
        top = request.POST.get('top')    # Retrieve top value

        # Save the table location to the database
        table = Table.objects.get(id=table_id)
        table.left = left  # Update left value
        table.top = top    # Update top value
        table.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def bookings_management(request):

    """Handles the table creation form of just the table size input."""
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.save()
            messages.success(request, 'New table added to seating plan.')
            return redirect('bookings_management')
    else:
        form = TableForm()

    def next_day(date):
        """Returns the next day from a given date."""
        next_day = date + timedelta(days=1)
        return make_aware(datetime(next_day.year,
                          next_day.month, next_day.day, 0, 0, 0))

    tables = Table.objects.all().order_by('number')

    # Retrieve the table location data
    table_locations = []
    for table in tables:
        table_locations.append({
            'table_id': table.id,
            'left': table.left,
            'top': table.top
        })

    """Set the date range for filter"""
    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    next_week = today + timedelta(days=7)

    """Filter bookings by not earlier than the current day"""
    now = datetime.now()
    today = make_aware(datetime(now.year, now.month, now.day, 0, 0, 0))
    bookings = Booking.objects.filter(start_time__gte=today)

    """Get search query from request"""
    search_query = request.GET.get('search', '')

    """Get filter query from request"""
    filter_query = request.GET.get('filter', '')

    """Filter bookings by user name if search query is provided"""
    if search_query:
        bookings = bookings.filter(user__username__icontains=search_query)

    """Filter bookings by day or week if filter query is provided"""
    if filter_query == 'day':
        start_date = today
        end_date = start_date + timedelta(days=1)
        bookings = bookings.filter(
            start_time__range=(start_date, end_date)).order_by('start_time')
    elif filter_query == 'week':
        start_date = today
        end_date = start_date + timedelta(days=7)
        bookings = bookings.filter(
            start_time__range=(start_date, end_date)).order_by('start_time')

    """
    Annotate the query set
    with a truncated start_time field
    (day-level precision)
    """
    bookings = bookings.annotate(day=Trunc('start_time', 'day'))

    """Perform grouping by day and count the number of bookings per day"""
    grouped_results = bookings.values('day').annotate(count=Count('id'))

    for result in grouped_results:
        result['bookings'] = bookings.filter(start_time__date=result['day'])

    context = {
        'table_form': form,
        'grouped_results': grouped_results,
        'filter_query': filter_query,
        'search_query': search_query,
        'tables': tables,
        'table_locations': table_locations,
    }

    return render(request, 'bookings/bookings_management.html', context)


"""Simple model deletion with message.
    However, deletion of a table will result in the collapse
    of all associated bookings and time slots for all bookings
    through the cascade method.
    A warning should be implemented to the admin before aggreeing
    to delete a table. Alternatively the edit_booking function could be
    used to automatically attempt to reconstitute bookings keeping
    date/time and party-size unaltered."""


def delete_table(request, table_id):
    if not request.user.is_superuser:
        messages.error(
            request, "You are not authorised to delete a table.")
        return redirect('home')
    old_table = get_object_or_404(Table, id=table_id)
    table = get_object_or_404(Table, id=table_id)
    bookings = Booking.objects.filter(table=table)
    slots = TableAvailability.objects.filter(table=table)

    if not bookings and not slots:
        old_table.delete()
        return redirect(reverse('bookings_management'))

    tables = Table.objects.exclude(id=table.id).order_by('number')
    successful_bookings = []

    for booking in bookings:
        start_time = booking.start_time
        end_time = start_time + timedelta(minutes=105)
        size_of_party = booking.size_of_party

        for table in tables:
            table_availabilities = TableAvailability.objects.filter(
                table=table,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            # Check if the table sizes are compatible
            if size_of_party > int(table.size):
                continue

            # Check if the table size difference is valid
            if int(table.size) - size_of_party > 2:
                continue

            if not table_availabilities:
                # Delete the slot, create a new one, and update the booking
                TableAvailability.objects.filter(
                    booking_id=booking.id).delete()

                booking.end_time = start_time + timedelta(minutes=105)
                booking.table = table
                booking.start_time = start_time
                booking.save()

                table_availability = TableAvailability(
                    table=table,
                    start_time=start_time,
                    end_time=booking.end_time,
                    booking_id=booking,
                )
                table_availability.save()

                successful_bookings.append(booking)

    print(bookings, slots, tables, successful_bookings)

    if successful_bookings:
        old_table.delete()
        return redirect(reverse('bookings_management'))
    else:
        messages.error(request, "Failed to create new table availability. \
            Deletion canceled.")
        return redirect(reverse('bookings_management'))
