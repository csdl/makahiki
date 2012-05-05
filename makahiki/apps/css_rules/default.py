"""Provides variables (strings and dicts) that implement mappings of ids to CSS classes.

Templates that use class_tags and insert_classes refer to this module. Note that some of the "ids"
are more like class names.  These rules act like "macro expansions" in the templates. If True, the
classes will be inserted.  Otherwise, the tags will be empty strings.

Makahiki 2 note: CSS information specific to particular widgets should be encapsulated with that
widget.
"""

RETURN_CLASSES = True

CSS_IMPORTS = """
<link rel="stylesheet" href="{0}jquery-ui/jquery-ui.css">
"""

LOGGED_IN_CSS_IMPORT = '<link rel="stylesheet" ' \
                       'href="{0}css/{1}/logged_in_base.css">'

PAGE_CSS_IMPORT = {
    "home": '<link rel="stylesheet" href="{0}css/home.css">',
    "landing": '<link rel="stylesheet" href="{0}css/landing.css">',
    "news": '<link rel="stylesheet" href="{0}css/news'
            '.css">\n<script src="{0}js/news.js" '
            'type="text/javascript"></script>',
    "learn": '<link rel="stylesheet" href="{0}css/learn.css">',
    "energy": '<link rel="stylesheet" href="{0}css/energy'
              '.css">\n<script src="{0}js/news.js" '
              'type="text/javascript"></script>',
    "help": '<link rel="stylesheet" href="{0}css/help.css">',
    "win": '<link rel="stylesheet" href="{0}css/win.css">',
    "profile": '<link rel="stylesheet" href="{0}css/profile.css">',
    "advanced": '<link rel="stylesheet" href="{0}css/advanced.css">',
    "status": '<link rel="stylesheet" href="{0}css/status.css">',
    }

CSS_IDS = {
    "landing-sponsors": "content-box",
    "landing-sponsors-title": "content-box-title",

    "quest-list": "quest-list",

    "home-energy": "home-item",
    "home-activities": "home-item",
    "home-news": "home-item",
    "home-prizes": "home-item",
    "home-help": "home-item",
    "home-profile": "home-item",

    "energy-power": "content-box",
    "resource-scoreboard-box": "content-box",
    "energy-status-box": "content-box",
    "energy-power-title": "content-box-title",
    "resource-scoreboard-title": "content-box-title",
    "energy-status-title": "content-box-title",

    "activity-events-box": "content-box",
    "activity-scoreboard-box": "content-box",
    "activity-categories-box": "content-box",
    "activity-task-stats-box": "content-box",
    "activity-task-details-box": "content-box",
    "activity-events-title": "content-box-title",
    "activity-categories-title": "content-box-title",
    "activity-scoreboard-title": "content-box-title",
    "activity-task-stats-title": "content-box-title",
    "activity-task-details-title": "content-box-title",

    "news-wall": "content-box",
    "news-events": "content-box",
    "news-commitments": "content-box",
    "news-most-popular": "content-box",
    "news-members": "content-box",
    "news-wall-title": "content-box-title",
    "news-events-title": "content-box-title",
    "news-commitments-title": "content-box-title",
    "news-most-popular-title": "content-box-title",
    "news-members-title": "content-box-title",
    "team-members": "content-box",
    "team-members-title": "content-box-title",

    "help-video": "content-box",
    "help-rules": "content-box",
    "help-faq": "content-box",
    "help-ask": "content-box",
    "help-topic": "content-box",
    "help-video-title": "content-box-title",
    "help-rules-title": "content-box-title",
    "help-faq-title": "content-box-title",
    "help-ask-title": "content-box-title",
    "help-topic-title": "content-box-title",
    "help-video-content": "content-box-contents",
    "help-rules-content": "content-box-contents",
    "help-faq-content": "content-box-contents",
    "help-topic-content": "content-box-contents",

    "profile-form-box": "content-box",
    "profile-badges-box": "content-box",
    "profile-history-box": "content-box",
    "profile-commitments-box": "content-box",
    "profile-notifications-box": "content-box",
    "profile-form-title": "content-box-title",
    "profile-badges-title": "content-box-title",
    "profile-history-title": "content-box-title",
    "profile-notifications-title": "content-box-title",
    "profile-commitments-title": "content-box-title",
    "profile-form-fb-header": "profile-section-header",
    "profile-form-general-header": "profile-section-header",
    "profile-form-contact-header": "profile-section-header",
    "profile-form-display-name-label": "profile-form-label",
    "profile-form-picture-label": "profile-form-label",
    "profile-form-about-label": "profile-form-label",
    "profile-form-logged-in-label": "profile-form-label",
    "profile-form-fb-profile-label": "profile-form-label",
    "profile-form-contact-email-label": "profile-form-label",
    "profile-form-contact-text-label": "profile-form-label",

    "badge-catalog-box": "content-box",
    "badge-catalog-title": "content-box-title",

    "avatar-change": "content-box",
    "avatar-change-title": "content-box-title",

    "prizes-list": "content-box",
    "prizes-raffle": "content-box",
    "prizes-raffle-title": "content-box-title",
    "prizes-list-title": "content-box-title",

    "canopy-quests": "content-box",
    "canopy-quests-title": "content-box-title",
    "canopy-viz": "content-box",
    "canopy-viz-title": "content-box-title",
    "canopy-feed": "content-box",
    "canopy-feed-title": "content-box-title",
    "canopy-members": "content-box",
    "canopy-members-title": "content-box-title",
    "canopy-karma": "content-box",
    "canopy-karma-title": "content-box-title",
    }

CSS_CLASSES = {
    "system-post": "news-system-post",
    "system-post-date-string": "news-system-posted",
    "system-post-content": "news-system-text",
    "user-post-avatar": "news-image",
    "user-post-content": "news-text",
    "user-post-date-string": "news-posted",
    "activity-categories-title": "activity-categories-title",
    "prize-item": "prize",
    "prize-number": "number",
    "prize-dialog": "prize-dialog",
    }
