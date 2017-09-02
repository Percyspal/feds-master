from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm, PasswordConfirmationForm
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
        # Show form again, with bad user data.
        return render(request,
                      'registration/register.html',
                      {'user_form': user_form}
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
        # Make a form for the user's password.
        password_form = PasswordConfirmationForm(data=request.POST)
        # Make a form for the current user object.
        user_form = UserEditForm(instance=request.user, data=request.POST)
        # Make a form for the profile additions.
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if password_form.is_valid() and user_form.is_valid() and profile_form.is_valid():
            # Check that the password is correct.
            password_entered = password_form.cleaned_data['password_confirmation']
            # Check if Django trims
            if request.user.check_password(password_entered):
                # Password correct. Save data.
                user_form.save()
                profile_form.save()
                return redirect('accounts:user_deets')
            # Password not correct.
            messages.error(request, 'Wrong password.')
    elif request.method == 'GET':
        # It's a GET
        # Make a form for the user's password.
        password_form = PasswordConfirmationForm()
        # Make a form for the current user object.
        user_form = UserEditForm(instance=request.user)
        # Make a form for the profile additions.
        profile_form = ProfileEditForm(instance=request.user.profile)
    else:
        # Not a get or post.
        raise SuspiciousOperation('Bad HTTP op in user edit: {op}'.format(op=request.method))
    return render(request,
                  'registration/user_edit.html',
                  {
                      'password_form': password_form,
                      'user_form': user_form,
                      'profile_form': profile_form
                  }
                  )


@login_required
def user_deets(request):
    return render(request, 'registration/user_deets.html', {'user': request.user, })


@login_required
def delete_account(request):
    return HttpResponse('Not implemented yet')
    # return render(request, 'registration/user_delete.html', {'user': request.user, })
