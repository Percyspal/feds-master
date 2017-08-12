import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project


class ProjectModelTests(TestCase):

    def setUp(self):
        """ Make some users to be project owners. """
        self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')

    def test_unique_slug_ok(self):
        """ Slug for only project for user is not changed. """
        p = Project()
        p.user = self.u1
        p.title = "This is a title"
        p.save()
        self.assertEqual(p.slug, "this-is-a-title")
        self.assertFalse(p.slug_changed)

    def test_repeated_slug_updated(self):
        """ Same slug for project for same user is changed. """
        p1 = Project()
        p1.user = self.u1
        p1.title = "This is a title"
        p1.save()
        p2 = Project()
        p2.user = self.u1
        p2.title = "This is a title"
        p2.save()
        self.assertNotEqual(p2.slug, p1.slug)
        self.assertTrue(p2.slug_changed)

    def test_same_slug_different_users(self):
        """ Same slug for different users is not changed. """
        p1 = Project()
        p1.user = self.u1
        p1.title = "This is a title"
        p1.save()
        p2 = Project()
        p2.user = self.u2
        p2.title = "This is a title"
        p2.save()
        self.assertEqual(p2.slug, p1.slug)
        self.assertFalse(p2.slug_changed)

    def test_repeated_repeated_slug_updated(self):
        """ Same slug for user repeated twice. """
        title = "This is a title"
        p1 = Project()
        p1.user = self.u1
        p1.title = title
        p1.save()
        p2 = Project()
        p2.user = self.u1
        p2.title = title
        p2.save()
        p3 = Project()
        p3.user = self.u1
        p3.title = title
        p3.save()
        self.assertNotEqual(p1.slug, p2.slug)
        self.assertNotEqual(p1.slug, p3.slug)
        self.assertNotEqual(p2.slug, p3.slug)
        self.assertTrue(p2.slug_changed)
        self.assertTrue(p3.slug_changed)

    def test_need_user_for_project(self):
        """ Project must have a user. """
        with self.assertRaises(Exception):
            p = Project()
            p.title = "DOG!"
            p.save()

    def test_date_created_set(self):
        """ Project saved the sate it was created. """
        p = Project()
        p.title = "DOG!"
        p.user = self.u1
        p.save()
        self.assertEqual(p.when_created, datetime.date.today())

    def test_need_title_for_project(self):
        """ Project must have a title. """
        with self.assertRaises(Exception):
            p = Project()
            p.user = self.u1
            p.save()

    def test_title_trimmed(self):
        """ Title is trimmed. """
        p = Project()
        p.title = "  DOG!  "
        p.user = self.u1
        p.save()
        self.assertEqual(p.title, p.title.strip())

    def test_description_trimmed(self):
        """ Description is trimmed. """
        p = Project()
        p.title = "DOG!"
        p.user = self.u1
        p.description = "  Dogs are the best!  "
        p.save()
        self.assertEqual(p.description, p.description.strip())
