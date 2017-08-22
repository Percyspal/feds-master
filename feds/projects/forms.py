from django import forms
from feds.settings import FEDS_REST_HELP_URL
from businessareas.models import BusinessAreaDb
from .models import ProjectDb


class ProjectForm(forms.ModelForm):
    # Specify business_area field, so can omit MT choice from <select>.
    business_area = forms.ModelChoiceField(
        BusinessAreaDb.objects.all().order_by('title'),
        empty_label=None
    )

    class Meta:
        model = ProjectDb
        fields = ('title', 'slug', 'description', 'business_area', )


class ConfirmDeleteForm(forms.Form):
    """ A form to confirm deleting a project. """
    confirm = forms.BooleanField(
        initial=False,
        required=False,  # Needed for this to work.
        label='Confirm delete',
        help_text='Are you sure you want to delete the project?'
    )
