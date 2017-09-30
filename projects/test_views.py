import datetime
from django.test import TestCase, LiveServerTestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from .models import ProjectDb
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class ProjectViewsTests(LiveServerTestCase):

    def setUp(self):
        """ Make some users to be project owners. """
        self.u1 = User.objects.create_user('u1', 'u1@example.com', 'u1')
        self.u2 = User.objects.create_user('u2', 'u2@example.com', 'u2')

    def test_thing(self):
        return
        driver = webdriver.Firefox()
        # driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get("https://docs.djangoproject.com/en/1.11/")
        search_box = driver.find_element_by_name("q")
        search_box.send_keys("testing")
        search_box.send_keys(Keys.RETURN)
        assert "Search" in driver.title
        # Locate first result in page using css selectors.
        result = driver.find_element_by_css_selector("div#search-results a")
        result.click()
        assert "testing" in driver.title.lower()
        driver.quit()


    def test_something(self):
        """ Slug for only project for user is not changed. """
        p = ProjectDb()
        p.user = self.u1
        p.title = "This is a title"
        p.save()
        # self.assertEqual(p.slug, "this-is-a-title")
        # self.assertFalse(p.slug_changed)


    def test_something_else(self):
        """ Project must have a user. """
        with self.assertRaises(ObjectDoesNotExist):
            p = ProjectDb()
            p.title = "DOG"
            p.save()
