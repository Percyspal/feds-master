from django.shortcuts import render, redirect
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.contrib import messages
from helpers.form_helpers import extract_model_field_meta_data
from .forms import ContactForm
from .models import ContactFormMessage

def contact_page(request):
    if request.method == 'GET':
        form = ContactForm(
            initial={'contact_name': '', 'contact_email': '', 'message': ''})
        captcha = 'yes'
        if request.user.is_authenticated():
            captcha = 'no'
        context = {
            'form': form,
            'captcha': captcha,
            # Grab model field metadata not available to templates.
            'model_field_meta_data':
                extract_model_field_meta_data(form,
                                              ['help_text', 'max_length']),
        }
        return render(
            request,
            'contact/contact.html',
            context
        )
    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = ContactFormMessage()
            contact.contact_name = form.cleaned_data['contact_name']
            contact.contact_email = form.cleaned_data['contact_email']
            contact.message = form.cleaned_data['message']
            form.save()
            messages.success(request, 'Message sent.')
            return redirect('contact')
        # Show form again, with bad user data.
        return render(
            request,
            'contact/contact.html',
            {
                'form': form,
                # Grab model field metadata not available to templates.
                'model_field_meta_data':
                    extract_model_field_meta_data(form,
                                                  ['help_text', 'max_length']),
            }
        )
    else:
        raise SuspiciousOperation(
            'Bad HTTP op in create_edit_project: {op}'.format(
                op=request.method))
