"""Defines the Quest Model."""

import datetime
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from apps.managers.cache_mgr import cache_mgr
from apps.managers.score_mgr import score_mgr
from apps.managers.predicate_mgr import predicate_mgr


class Quest(models.Model):
    """Represents a quest in the database."""
    name = models.CharField(max_length=255, help_text="The name of the quest.")
    quest_slug = models.SlugField(help_text="A unique identifier of the quest. Automatically "
                                            "generated if left blank.")
    description = models.TextField(
        help_text="Discription of the quest. It should outline the steps to completing"
                  " this quest. %s" % settings.MARKDOWN_TEXT)
    priority = models.IntegerField(
        default=1,
        help_text="Quest with lower values (higher priority) will be listed first."
    )
    unlock_conditions = models.TextField(
        help_text="Conditions a user needs to meet in order to have this quest be"
                  " available (appeared in the Quest widget). " +
                  settings.PREDICATE_DOC_TEXT
    )
    completion_conditions = models.TextField(
        help_text="Conditions a user needs to meet in order to complete the quest. " +
                  settings.PREDICATE_DOC_TEXT
    )
    users = models.ManyToManyField(User, through="QuestMember")

    def __unicode__(self):
        return self.name

    def can_add_quest(self, user):
        """Returns True if the user can add the quest."""
        return predicate_mgr.eval_predicates(self.unlock_conditions, user)

    def completed_quest(self, user):
        """Returns True if the user completed the quest."""
        return predicate_mgr.eval_predicates(self.completion_conditions, user)

    def accept(self, user):
        """Lets the user accept the quest.  Returns True if successful."""
        # Check if user can add the quest.
        if not self.can_add_quest(user):
            return False

        # Check if this quest is in their list of quests.
        if self in user.quest_set.all():
            return False

        member = QuestMember(quest=self, user=user)
        member.save()
        return True

    def opt_out(self, user):
        """Lets the user opt out of seeing the quest.  Returns True if successful."""
        # Check if user can add the quest.
        if not self.can_add_quest(user):
            return False

        # Note in this case, we don't care if the user already has the quest.
        member, _ = QuestMember.objects.get_or_create(quest=self, user=user)
        member.opt_out = True
        member.save()
        return True


class QuestMember(models.Model):
    """Represents a user's participation in a quest.
       Shouldn't be in the admin interface, since there shouldn't be a reason to edit instances."""
    user = models.ForeignKey(User)
    quest = models.ForeignKey(Quest)
    completed = models.BooleanField(default=False,
        help_text="True if the user completed the quest.")
    opt_out = models.BooleanField(default=False,
        help_text="True if the user opts out of the quest.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """meta"""
        unique_together = ["user", "quest"]

    def save(self, *args, **kwargs):
        """Custom save method to create a points transaction after the object is saved."""
        super(QuestMember, self).save(*args, **kwargs)
        if self.completed:
            message = "Quest: %s" % self.quest.name
            self.user.profile.add_points(score_mgr.quest_points(),
                                               datetime.datetime.today(), message, self)
        cache_mgr.delete('get_quests-%s' % self.user.username)

    def delete(self, *args, **kwargs):
        """Custom delete method."""
        cache_mgr.delete('get_quests-%s' % self.user.username)
        super(QuestMember, self).delete(*args, **kwargs)
