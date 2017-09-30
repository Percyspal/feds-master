from django.contrib.auth.models import User
from django import forms
from captcha.fields import ReCaptchaField
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        # https://stackoverflow.com/questions/39600784/django-1-9-check-if-email-already-exists
        email = self.cleaned_data.get('email')
        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email
        # A user was found with this as a username, raise an error.
        raise forms.ValidationError(
            'Sorry, this email address is already in use.')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('about', 'web_site')


class PasswordConfirmationForm(forms.Form):
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput,
        help_text='Your need to enter your password to make any changes.',
        required=True
    )
