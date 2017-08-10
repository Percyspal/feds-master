from django.db import models
from django.core.exceptions import ValidationError

class FieldSpec():
    """ Base class for all field specifications. """
    def __init__(self, title):
        self.title = title

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        title = title.strip()
        if not title:
            raise ValidationError('FieldSpec title cannot be blank.')
        self.__title = title


class PrimaryKeyFieldSpec(FieldSpec):
    """ A primary key field specification. """
    def __init__(self, title):
        super().__init__(title)
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

