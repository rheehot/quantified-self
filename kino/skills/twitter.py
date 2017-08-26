
import twitter

from ..slack.slackbot import SlackerAdapter

from ..utils.config import Config



class TwitterManager:

    MAX_TEXT_LENGTH = 138
    MAX_LINK_LENGTH = 90

    def __init__(self, slackbot=None):
        config = Config()
        self.api = twitter.Api(consumer_key=config.open_api["twitter"]["CONSUMER_KEY"],
                  consumer_secret=config.open_api["twitter"]["CONSUMER_SECRET"],
                  access_token_key=config.open_api["twitter"]["ACCESS_TOKEN_KEY"],
                  access_token_secret=config.open_api["twitter"]["ACCESS_TOKEN_SECRET"])

        if slackbot is None:
            self.slackbot = SlackerAdapter(channel=config.channel.get('FEED', '#general'))
        else:
            self.slackbot = slackbot

    def tweet(self, text: str) -> None:
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[:self.MAX_TEXT_LENGTH - 3] + "..."
        self.api.PostUpdate(text)

    def feed_tweet(self, feed: tuple) -> None:
        tweet_title = "#kino_bot, #feed"
        title, link, _ = feed

        if len(link) > self.MAX_LINK_LENGTH:
            return

        remain_text_length = MAX_TEXT_LENGTH - len(tweet_title) - len(link)

        if len(title) > remain_text_length:
            title = title[:remain_text_length - 3] + "..."

        self.tweet(f"{tweet_title}\n{title}\n{link}")

    def reddit_tweet(self, reddit: str) -> None:
        tweet_title = "#kino_bot, #reddit"

        self.tweet(f"{tweet_title}\n{reddit}")

