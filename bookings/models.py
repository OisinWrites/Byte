from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# The table model
# Three different sizes of tables, unique ids, and boolean for availability
class Table(models.Model):
    TABLE_SIZES = (
        ('2', '2-seater'),
        ('4', '4-seater'),
        ('6', '6-seater'),
    )
    number = models.IntegerField(unique=True)
    size = models.CharField(max_length=1, choices=TABLE_SIZES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'Table {self.number} ({self.get_size_display()})'


# The booking model
# Takes a table as a FK, generates an end time based on its start time
# in the corresponding view. Takes email of user to verify what
# bookings are accesssible to a authorised user later, takes a name as
# a friendly version of email for that template,
# takes in size of party to reflect to admin that a booking at
# a table of 6 could be for 4 or 5 pax.
class Booking(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    user_email = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE)
    user_name = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='bookings')
    size_of_party = models.IntegerField()
    additional = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user_name.username} ({self.size_of_party} people)' \
               f' - {self.table} ' \
               f'- {self.start_time.strftime("%d-%m %H:%M")} to ' \
               f'{self.end_time.strftime("%d-%m %H:%M")}'


# This table availability model is to track the tables availability at 
# given time and date, and presuming a table is otherwise always available in
# the table model. The old boolean could be used for the admin to 
# temporarily remove a table from being available for bookings, eg:
# reserved for walk-ins.
class TableAvailability(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
