import curses
from argparse import ArgumentParser

from praw import Reddit  # type: ignore

from redditmoddingsucks.moderation.moderation import RedditModeration
from redditmoddingsucks.settings import settings
from redditmoddingsucks.ui.user_interface import UserInterface


def modqueue_client():
    """modqueue_client is a function that runs the modqueue client."""
    parser = ArgumentParser()
    parser.add_argument(
        "--subreddit",
        type=str,
        help="Subreddit which your poor soul moderates",
        required=True,
    )
    args, _ = parser.parse_known_args()
    reddit = Reddit(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        password=settings.password,
        username=settings.username,
        redirect_uri=settings.redirect_uri,
        user_agent=settings.user_agent,
    )

    ui = UserInterface(RedditModeration(reddit, args.subreddit))
    curses.wrapper(ui)
