from django.db import models


class ContactFormMessage(models.Model):
    contact_name = models.CharField(
        verbose_name='Your name',
        blank=False,
        max_length=50,
        help_text='Your name',
    )
    contact_email = models.EmailField(
        verbose_name='Your email',
        blank=False,
        max_length=254,
        help_text='Your email address',
    )
    message = models.TextField(
        blank=False,
        max_length=10000,
        help_text='What do you want to say?'
    )
    when_sent = models.DateField(
        auto_now=True,
        db_index=True
    )

    def __str__(self):
        return 'Message from {name} on {when}'.format(name=self.contact_name, when=self.when_sent)
