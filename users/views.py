from django.shortcuts import render, redirect
from django.contrib.auth import login
from .custom_forms import SignUpForm


# Create your views here.
from .models import Profile


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form
        form = SignUpForm()
    else:
        # Process completed form
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            # Get phone number
            phone = form.cleaned_data.get('phone_number')
            isDriver = form.cleaned_data.get('is_driver')

            # Save new user to db, post_save signal creates Profile instance
            new_user = form.save()

            # # Get Profile instance
            new_profile = Profile.objects.get(user=new_user)
            new_profile.phone_number = phone
            new_profile.is_driver = isDriver
            new_profile.save()
            # Log the user in and redirect to home page
            login(request, new_user)
            return redirect('main:index')

    # Display a blank or invalid form
    context = {'form': form}
    return render(request, 'registration/register.html', context)
