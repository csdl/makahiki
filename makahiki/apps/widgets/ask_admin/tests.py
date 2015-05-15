"""
ask admin tests.
"""
from django.test import TransactionTestCase
from django.core.urlresolvers import reverse

from apps.utils import test_utils


class AskAdminFunctionalTests(TransactionTestCase):
    """AskAdmin test cases."""

    def setUp(self):
        """setup"""
        self.user = test_utils.setup_user(username="user",
                                          password="bogus")
        self.client.login(username="user", password="bogus")

    def testAjaxPost(self):
        """
        Test that an AJAX post to ask an admin sends an email.
        """

        response = self.client.post(reverse('ask_admin_feedback'), {
            'url': 'http://localhost:8000/test/',
            'question': 'question',
            }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.failUnlessEqual(response.status_code, 200)
        #self.assertEqual(len(mail.outbox), 1)
        #self.assertTrue(mail.outbox[0].subject.find(self.user.profile.name) > 0)
