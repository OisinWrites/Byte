from django.contrib import admin
from .models import Booking, Table

# Register your models here.


class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'table',
        'start_time',
        'end_time',
        'email',
        'user_name',
        'size_of_party',
    )


class TableAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'size',
        'is_available',
    )


# Register your models here.
admin.site.register(Booking, BookingAdmin,)
admin.site.register(Table, TableAdmin,)
