from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ProfileRegisterForm
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


# Create your views here.


def register(request):
    """Register a new user."""

    if request.method != 'POST':
        # Display blank registration form
        user_form = UserCreationForm()
        profile_form = ProfileRegisterForm()
    else:
        # Process completed form
        user_form = UserCreationForm(data=request.POST)
        profile_form = ProfileRegisterForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():

            # Get phone number
            phone = profile_form.cleaned_data.get('phone')

            # Save new user to db, post_save signal creates Profile instance
            new_user = user_form.save()

            # Get Profile instance
            new_profile = Profile.objects.get(user=new_user)
            new_profile.phone_number = phone
            new_profile.save()

            # Log the user in and redirect to home page
            login(request, new_user)
            return redirect('main:index')

    # Display a blank or invalid form
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'registration/register.html', context)
