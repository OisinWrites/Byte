from django import forms
from bookings.models import Booking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Field


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['table', 'start_time', 'size_of_party']

        crispy_layout = Layout(
            Field('table', css_class='form-control'),
            Field('start_time', css_class='form-control'),
            Field('size_of_party', css_class='form-control'),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_method = 'post'
        self.helper.form_action = 'bookings'
        self.helper.form_class = 'form-horizontal'
