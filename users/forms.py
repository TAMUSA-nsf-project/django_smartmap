from django.core.validators import RegexValidator
from django import forms

from .models import Profile


class ProfileRegisterForm(forms.ModelForm):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits "
                                         "allowed.")
    phone = forms.CharField(validators=[phone_regex], max_length=17)

    class Meta:
        model = Profile
        fields = ['phone']
