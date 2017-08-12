from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('title', 'slug', 'description', )


class ConfirmDeleteForm(forms.Form):
    """ A form to confirm deleting a project. """
    confirm = forms.BooleanField(
        initial=False,
        required=False,  # Needed for this to work.
        label='Confirm delete',
        help_text='Are you sure you want to delete the project?'
    )
