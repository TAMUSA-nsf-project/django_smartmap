from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from django import forms


class SignUpForm(UserCreationForm):
    username = forms.CharField(label="Username", min_length=5, max_length=195)
    email = forms.EmailField(label='email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    phone_number = PhoneNumberField(label="Enter Phone Number")
    is_driver = forms.fields.BooleanField(label="I want to register as a Bus Driver")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['is_driver'].initial = False

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def username_clean(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError("User Already Exist")
        return username

    def email_clean(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(" Email Already Exist")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        return user
