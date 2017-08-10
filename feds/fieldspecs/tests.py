from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import FieldSpec, PrimaryKeyFieldSpec


class FieldSpecTests(TestCase):

    def test_title_ok(self):
        t1 = FieldSpec('New title')
        self.assertEquals(t1.title, 'New title')

    def test_empty_title(self):
        with self.assertRaises(ValidationError):
            t1 = FieldSpec('')

    def test_whitespace_title(self):
        with self.assertRaises(ValidationError):
            t1 = FieldSpec('  ')

    def test_primary_key_title_ok(self):
        t1 = PrimaryKeyFieldSpec('New title')
        self.assertEquals(t1.title, 'New title')

    def test_empty_primary_key_title(self):
        with self.assertRaises(ValidationError):
            t1 = PrimaryKeyFieldSpec('')

    def test_whitespace_primary_key_title(self):
        with self.assertRaises(ValidationError):
            t1 = PrimaryKeyFieldSpec('   ')
