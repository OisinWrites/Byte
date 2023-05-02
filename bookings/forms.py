from django import forms
from django.core.exceptions import ValidationError
from bookings.models import Booking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django.forms.widgets import DateTimeInput
from datetime import datetime, time


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'size_of_party', 'additional']
        widgets = {
            'user': forms.HiddenInput(),
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'})
        }

        crispy_layout = Layout(
            Field('start_time', css_class='form-control'),
            Field('size_of_party', css_class='form-control'),
            Field('additional', css_class='form-control'),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_method = 'post'
        self.helper.form_action = 'bookings'
        self.helper.form_class = 'form-horizontal'

        # Set validators for start_time field
        self.fields['start_time'].validators.append(self.validate_start_time)

    def validate_start_time(self, value):
        """
        Custom validator for start_time field to limit
        available days to all but Monday and Tuesday
        and set start times from 17:00 to 21:00.
        """
        if value.weekday() in [0, 1]:  # Monday is 0, Tuesday is 1
            raise ValidationError("Bookings are not available\
                 on Monday or Tuesday.")
        if value.time() < time(hour=17) or value.time() >= time(hour=21):
            raise ValidationError("Seating is only\
                 available from 17:00 to 21:00.")
