from django.contrib import admin
from .models import Booking, Table, TableAvailability

# Register your models here.


class TableAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'table',
        'start_time',
        'end_time',
        'booking_id',
    )


class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'email',
        'id',
        'table',
        'start_time',
        'end_time',
        'size_of_party',
        'additional',
    )

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'User'


class TableAdmin(admin.ModelAdmin):
    list_display = (
        'size',
        'number',
    )


# Register your models here.
admin.site.register(Booking, BookingAdmin,)
admin.site.register(Table, TableAdmin,)
admin.site.register(TableAvailability, TableAvailabilityAdmin,)
