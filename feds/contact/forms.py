from django import forms
from .models import ContactFormMessage
from captcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    contact_name = forms.CharField()
    contact_email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField()
