from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserProfileForm
from .models import Profile


# Create your views here.


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form
        form = UserProfileForm()
    else:
        # Process completed form
        form = UserProfileForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()

            # Create Profile object
            phone = request.POST.get('phone')
            Profile.objects.create(phone_number=phone, user=new_user)

            # Log the user in and redirect to home page
            login(request, new_user)
            return redirect('main:index')

    # Display a blank or invalid form
    context = {'form': form}
    return render(request, 'registration/register.html', context)
