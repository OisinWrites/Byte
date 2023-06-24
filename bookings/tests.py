from django.test import TestCase


from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from .models import Table, Booking
from .forms import TableForm


class BookingsManagementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpass')

    def setUp(self):
        self.assertEqual(self.user.username, 'testuser')
        self.table = Table.objects.create(number=1, size=4)
        self.booking = Booking.objects.create(
            user=self.user, table=self.table, size_of_party=4,
            start_time=datetime.now())

    def test_table_creation_form(self):
        url = reverse('bookings_management')
        response = self.client.post(url, {'number': 2, 'size': 6})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Table.objects.count(), 2)

    def test_bookings_filter_by_search(self):
        url = reverse('bookings_management')
        response = self.client.get(url, {'search': 'john'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.user.username)

    def test_bookings_filter_by_day(self):
        url = reverse('bookings_management')
        response = self.client.get(url, {'filter': 'day'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.user.username)

    def test_bookings_filter_by_week(self):
        url = reverse('bookings_management')
        response = self.client.get(url, {'filter': 'week'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.user.username)

    def test_bookings_filter_by_all(self):
        url = reverse('bookings_management')
        response = self.client.get(url, {'filter': 'all'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.user.username)

    def test_table_form_valid(self):
        form_data = {'number': 2, 'size': 6}
        form = TableForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_table_form_invalid(self):
        form_data = {'number': '', 'size': 6}
        form = TableForm(data=form_data)
        self.assertFalse(form.is_valid())


class DeleteBookingTestCase(TestCase):
    def setUp(self):
        table_id = 1
        table_queryset = Table.objects.filter(id=table_id)
        if table_queryset.exists():
            table = table_queryset.first()
        booking = Booking.objects.create(
            user=request.user,
            table=table,
            start_time='2023-05-06 10:00',
            end_time='2023-05-06 11:00'
            )
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.booking = Booking.objects.create(
            user=self.user, table=1, start_time='2023-05-06 10:00',
            end_time='2023-05-06 11:00')

    def test_delete_booking(self):
        url = reverse('delete_booking', args=[self.booking.id])
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(url, follow=True)

        # Check that the booking and table availability were deleted
        self.assertQuerysetEqual(
            Booking.objects.filter(id=self.booking.id), [])
        self.assertQuerysetEqual(
            TableAvailability.objects.filter(
                table=self.booking.table,
                start_time=self.booking.start_time,
                end_time=self.booking.end_time),
            [])

        # Check that success message is displayed and user is redirected
        self.assertContains(response, 'Your booking has been deleted.')
        self.assertRedirects(response, reverse('bookings'))
