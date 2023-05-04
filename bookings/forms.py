from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.forms.widgets import DateTimeInput


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from datetime import datetime, time

from bookings.models import Booking, Table


class BookingForm(forms.ModelForm):
    user_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Booking
        fields = ['start_time', 'size_of_party', 'additional']
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].initial = request.user.id
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_method = 'post'
        self.helper.form_action = 'bookings'
        self.helper.form_class = 'form-horizontal'

        # Set validators for start_time field
        self.fields['start_time'].validators.append(self.validate_start_time)

        # Set validator for size_of_party field
        self.fields['size_of_party'].validators.append(MinValueValidator(1))

    def validate_start_time(self, value):
        """
        Custom validator for start_time field to limit available days
        to all but Monday and Tuesday
        and set start times from 17:00 to 21:00.
        """
        if value.weekday() in [0, 1]:  # Monday is 0, Tuesday is 1
            raise ValidationError("Bookings are not available"
                                  " on Monday or Tuesday.")
        if value.time() < time(hour=17) or value.time() >= time(hour=21):
            raise ValidationError("Bookings are only available"
                                  " from 17:00 to 21:00.")


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('number', 'size', 'is_available')
