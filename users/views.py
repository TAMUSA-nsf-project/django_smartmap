from django.shortcuts import render, redirect
from django.contrib.auth import login
from .custom_forms import CreateUserForm


# Create your views here.


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form
        form = CreateUserForm()
    else:
        # Process completed form
        form = CreateUserForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # Log the user in and redirect to home page
            login(request, new_user)
            return redirect('main:index')

    # Display a blank or invalid form
    context = {'form': form}
    return render(request, 'registration/register.html', context)
