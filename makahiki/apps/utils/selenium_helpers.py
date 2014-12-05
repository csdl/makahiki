"""Base class for Selenium tests used to keep things DRY."""

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from selenium.webdriver.firefox.webdriver import WebDriver


class MakahikiSeleniumTestCase(LiveServerTestCase):
    """
    Base class for Selenium tests. Use this instead of the LiveServerTestCase so that the setup
    and teardown is done for you. This also implements a helper method for logging in and logging
    out.
    """
    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        cls.selenium = WebDriver()
        super(MakahikiSeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Tear down for all tests in this class."""
        cls.selenium.quit()
        super(MakahikiSeleniumTestCase, cls).tearDownClass()

    def login(self, username, password):
        """Log in using the standard login."""
        self.selenium.get('%s%s' % (self.live_server_url, reverse("account_login")))
        self.selenium.find_element_by_id("id_username").clear()
        self.selenium.find_element_by_id("id_username").send_keys(username)
        self.selenium.find_element_by_id("id_password").clear()
        self.selenium.find_element_by_id("id_password").send_keys(password)
        self.selenium.find_element_by_css_selector("input[type=\"submit\"]").click()

    def logout(self):
        """Logout through the logout url."""
        self.selenium.get('%s%s' % (self.live_server_url, reverse("account_logout")))
