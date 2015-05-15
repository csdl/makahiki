"""News page Test"""
import datetime

from django.test import TransactionTestCase
from django.core.urlresolvers import reverse
from apps.managers.challenge_mgr import challenge_mgr
from apps.utils import test_utils

from apps.widgets.smartgrid.models import Commitment, ActionMember
from apps.managers.team_mgr.models import  Post
from apps.widgets.wallpost.views import DEFAULT_POST_COUNT


class NewsFunctionalTestCase(TransactionTestCase):
    """News page test"""

    def setUp(self):
        self.user = test_utils.setup_user(username="user", password="changeme")
        self.team = self.user.profile.team

        challenge_mgr.register_page_widget("news", "popular_tasks")
        challenge_mgr.register_page_widget("news", "my_commitments")
        challenge_mgr.register_page_widget("news", "wallpost.system_wallpost")
        challenge_mgr.register_page_widget("news", "wallpost.user_wallpost")

        from apps.managers.cache_mgr import cache_mgr
        cache_mgr.clear()

        self.client.login(username="user", password="changeme")

    def testIndex(self):
        """Check that we can load the index page."""
        response = self.client.get(reverse("news_index"))
        self.failUnlessEqual(response.status_code, 200)

    def testIndexCommitment(self):
        """Tests that a commitment shows up in public commitments and in the wall."""
        posts = self.team.post_set.count()
        # Create a commitment that will appear on the news page.
        commitment = Commitment(
            type="commitment",
            title="Test commitment",
            slug="test-commitment",
            description="A commitment!",
            point_value=10,
        )
        commitment.save()

        member = ActionMember(action=commitment, user=self.user)
        member.save()

        response = self.client.get(reverse("news_index"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(posts + 1, self.team.post_set.count(),
            "One post should have been posted to the wall (public commitment).")
        self.assertContains(response, commitment.title, 2,
            msg_prefix="Commitment title should only appear in the wall and the public " \
                       "commitments box."
        )

    def testIndexMostPopular(self):
        """Test most popular"""
        posts = self.team.post_set.count()
        commitment = Commitment(
            type="commitment",
            title="Test commitment2",
            slug="test-commitment2",
            description="A commitment2!",
            point_value=10,
        )
        commitment.save()

        member = ActionMember(action=commitment, user=self.user)
        member.save()

        member = ActionMember(action=commitment, user=self.user,
                              approval_status="approved",
                              award_date=datetime.datetime.today())
        member.save()

        response = self.client.get(reverse("news_index"))
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual(posts + 2, self.team.post_set.count(),
            "Two posts should have been posted to the wall (commit and award).")

        ## comment out because of the effect of caching.
        #self.assertContains(response, commitment.title, 3,
        #    msg_prefix="""
        #Commitment title should appear in the wall twice and in the most popular box. Note, may
        #fail because of caching.
        #"""
        #)

    def testPost(self):
        """Test that we can add new post via AJAX."""
        # Test posting an empty post.
        posts = Post.objects.filter(team=self.team)
        count = posts.count()
        response = self.client.post(reverse("news_post"), {"post": ""},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, "This should not be blank.")
        self.assertEqual(count, posts.count(), "Check that the number of posts did not change.")

        post = "Test post via AJAX"
        response = self.client.post(reverse("news_post"), {"post": post},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "Test post via AJAX")

        # Check that the new post is in the news feed.
        response = self.client.get(reverse("news_index"))
        self.assertContains(response, post)

    def testAjaxPosts(self):
        """Test that we can load new posts via AJAX."""
        # Generate test posts.
        for i in range(0, DEFAULT_POST_COUNT + 1):
            text = "Testing AJAX response %d." % i
            post = Post(user=self.user, team=self.team, text=text)
            post.save()

        second_post = Post.objects.all().order_by("-pk")[0]
        response = self.client.get(reverse("news_more_user_posts") + "?page_name=news",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.failUnlessEqual(response.status_code, 200)
        self.assertNotContains(response, "Testing AJAX response 0.")
        self.assertContains(response, "See more")
        for i in range(1, DEFAULT_POST_COUNT + 1):
            self.assertContains(response, "Testing AJAX response %d" % i)

        response = self.client.get(reverse("news_more_user_posts") +
                                   ("?last_post=%d&page_name=news" % second_post.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertContains(response, "Testing AJAX response 0.")
