from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django import forms

from users import models


class CreateUserForm(UserCreationForm):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits "
                                         "allowed.")
    phone = forms.CharField(validators = [phone_regex],max_length=17)
    is_driver = forms.fields.BooleanField(label="I want to register as a Bus Driver")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['is_driver'].initial = False

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'is_driver']

    def clean(self):
        cleaned_data = super(CreateUserForm, self).clean()
        phone = cleaned_data.get("phone")
        is_driver = cleaned_data.get("is_driver")
