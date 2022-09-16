from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField


class SignUpForm(UserCreationForm):
    phone_number = PhoneNumberField(label="Enter Phone Number")
    is_driver = forms.fields.BooleanField(label="I want to register as a Bus Driver", required=False)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['is_driver'].initial = 0

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']
