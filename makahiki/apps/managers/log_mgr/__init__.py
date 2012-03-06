"""Provides logging services to track the actions of players (logged in users)."""

import logging
from time import strftime  # Timestamp


def create_server_log(request, path=None):
    """Create a log entry for cases that logging middleware did not apply."""
    username = None
    if hasattr(request, "user") and request.user.is_authenticated():
        username = request.user.username

    if username:
        path = path or request.get_full_path()
        code = 200  # Hardcoded since this is obviously successful.
        method = "GET"
        ip_addr = request.META["REMOTE_ADDR"] if "REMOTE_ADDR" in request\
        .META else "no-ip"
        # Timestamp yyyy-mm-dd Time
        timestamp = strftime("%Y-%m-%d %H:%M:%S")

        # Create the log entry.
        entry = "%s %s %s %s %s %d" % (
        timestamp, ip_addr, username, method, path, code)

        logger = logging.getLogger("makahiki_logger")
        logger.info(entry)
