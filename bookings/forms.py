from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms.widgets import DateTimeInput
from django.forms.widgets import NumberInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.layout import Row, Column

from datetime import datetime, time

from bookings.models import Booking, Table


class BookingForm(forms.ModelForm):
    """Hides user id as a hidden form input, uneditable."""
    user_id = forms.IntegerField(widget=forms.HiddenInput())

    """Sets form fields
        Uses widget for calendar and time"""
    class Meta:
        model = Booking
        fields = ['start_time', 'size_of_party', 'additional']
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'}),
            'size_of_party': NumberInput(
                attrs={'type': 'range', 'min': 1, 'max': 6}),
            'additional': forms.Textarea(attrs={'rows': 5, 'cols': 30}),
        }

    """Sets behaviour for instance of booking"""
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].initial = request.user.id
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_method = 'post'
        self.helper.form_action = 'bookings'
        self.helper.form_class = 'form-horizontal'

        """Set validators for start_time field"""
        self.fields['start_time'].validators.append(self.validate_start_time)

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


"""Form to create tables in the management view"""


class TableForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('size', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = Table
        fields = ('size',)
        labels = {'size': 'Table Size'}
        widgets = {
            'size': forms.Select(attrs={'class': 'form-control'}),
        }
