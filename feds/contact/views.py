from django.shortcuts import render, redirect
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.contrib import messages
from helpers.form_helpers import extract_model_field_meta_data
from .forms import ContactForm


def contact_page(request):
    if request.method == 'GET':
        form = ContactForm(initial={'contact_name': '', 'contact_email': '', 'message': ''})
        return render(
            request,
            'contact/contact.html',
            {
                'form': form,
                # Grab model field metadata not available to templates.
                'model_field_meta_data':
                    extract_model_field_meta_data(form, ['help_text', 'max_length']),
            }
        )
    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Message sent.')
            form.save()
            return redirect('contact')
        # Show form again, with bad user data.
        return render(
            request,
            'contact/contact.html',
            {
                'form': form,
                # Grab model field metadata not available to templates.
                'model_field_meta_data':
                    extract_model_field_meta_data(form, ['help_text', 'max_length']),
            }
        )
    else:
        raise SuspiciousOperation('Bad HTTP op in create_edit_project: {op}'.format(op=request.method))
