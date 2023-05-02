from django.contrib import admin
from .models import Booking, Table

# Register your models here.


class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'table',
        'start_time',
        'end_time',
        'user',
        'size_of_party',
        'additional',
    )

    def get_username(self, obj):
        return obj.user_name.username
    get_username.short_description = 'User'


class TableAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'size',
        'is_available',
    )


# Register your models here.
admin.site.register(Booking, BookingAdmin,)
admin.site.register(Table, TableAdmin,)
