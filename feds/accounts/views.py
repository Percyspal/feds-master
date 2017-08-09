from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile


def feds_logout_view(request):
    """ Logout the user, and go back to home. """
    auth_views.logout(request)
    messages.success(request, 'Logged out')
    return redirect('home')


def feds_login_view(request, *args, **kwargs):
    """ Wrap standard auth login view to show message. """
    result = auth_views.login(request, *args, **kwargs)
    if request.user.is_authenticated():
        messages.success(request, 'Log in successful. Welcome, {0}.'.format(request.user.username))
    return result


def feds_password_change(request, *args, **kwargs):
    result = auth_views.password_change(request, *args, **kwargs)
    # import ipdb; ipdb.set_trace()
    return result


def feds_password_change_done(request, *args, **kwargs):
    result = auth_views.password_change_done(request, *args, **kwargs)
    return result


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the user profile
            profile = Profile.objects.create(user=new_user)
            # TODO: don't hard code path.
            return render(request,
                          'registration/register_done.html',
                          {'new_user': new_user}
                          )
    else:
        # GET: send the form.
        user_form = UserRegistrationForm()
        # TODO: don't hard code path.
        return render(request,
                      'registration/register.html',
                      {'user_form': user_form}
                      )

@login_required
def user_edit(request):
    if request.method == 'POST':
        # Make a form for the current user object.
        user_form = UserEditForm(instance=request.user, data=request.POST)
        # Make a form for the profile additions.
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        # It's a GET
        # Make a form for the current user object.
        user_form = UserEditForm(instance=request.user)
        # Make a form for the profile additions.
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request,
                  'registration/user_edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})