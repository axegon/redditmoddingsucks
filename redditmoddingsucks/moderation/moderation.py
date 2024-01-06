from praw import Reddit  # type: ignore

from redditmoddingsucks.moderation.base import AbstractModeration


class RedditModeration(AbstractModeration):
    """RedditModeration is a concrete implementation of AbstractModeration."""

    def __init__(self, reddit: Reddit, subreddit: str):
        self._reddit = reddit
        self._subreddit = subreddit

    @property
    def reddit(self):
        """RedditModeration.reddit is a property that returns the Reddit instance."""
        return self._reddit

    @property
    def subreddit(self):
        """RedditModeration.subreddit is a property that returns the subreddit."""
        return self._subreddit

    def fetch_mod_queue(self):
        """RedditModeration.fetch_mod_queue is a method that returns the mod queue."""
        return self.reddit.subreddit(self.subreddit).mod.modqueue(limit=None)

    def ban(self, user: str):
        """RedditModeration.ban is a method that bans a user.

        Args:
            user (str): The user to ban.
        """
        self.reddit.subreddit(self.subreddit).banned.add(user, ban_reason="")
