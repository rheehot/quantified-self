
import types

import langid
from slacker import Slacker

from .resource import MsgResource

from ..utils.config import Config
from ..utils.data_handler import DataHandler


class SlackerAdapter(object):

    def __init__(self, channel=None, user=None, input_text=None):
        self.config = Config()
        self.slacker = Slacker(self.config.slack['TOKEN'])
        self.channel = channel
        self.data_handler = DataHandler()

        self.user = user
        self.channel = channel

        if input_text is None:
            self.lang_code = config.bot["LANG_CODE"]
        else:
            self.lang_code = langid.classify(input_text)[0]

    def send_message(self, channel=None, text=None, attachments=None):
        if self.channel is None:
            self.channel = self.config.channel['DEFAULT']
        if channel is not None:
            self.channel = channel

        if isinstance(text, types.GeneratorType):
            print(self.lang_code)
            MsgResource.set_lang_code(self.lang_code)
            text = next(text)

        r = self.slacker.chat.post_message(
            channel=self.channel,
            text=text,
            attachments=attachments,
            as_user=True)
        self.data_handler.edit_cache(('message', r.body))

    def update_message(self, channel=None, text=None, attachments=None):
        if text is None:
            text = ""

        cache = self.data_handler.read_cache()
        if 'send_message' in cache:
            cache_message = cache['message']
            ts = cache_message['ts']
            channel = cache_message['channel']
            self.slacker.chat.update(ts=ts, channel=channel, text=text,
                                     attachments=attachments, as_user=True)
        else:
            self.send_message(
                text="마지막 메시지에 대한 정보가 없습니다.",
                channel=channel,
                as_user=True)

    def file_upload(self, f_name, channel=None, title=None, comment=None):
        if self.channel is None:
            self.channel = self.config.channel['DEFAULT']
        if channel is not None:
            self.channel = channel

        self.slacker.files.upload(
            f_name,
            channels=self.channel,
            title=title,
            initial_comment=comment)

    def start_real_time_messaging_session(self):
        response = self.slacker.rtm.start()
        return response.body['url']

    def get_bot_id(self):
        cache = self.data_handler.read_cache()
        if 'bot_id' in cache:
            return cache['bot_id']

        users = self.slacker.users.list().body['members']
        for user in users:
            if user['name'] == self.config.bot["BOT_NAME"].lower():
                bot_id = user['id']
                self.data_handler.edit_cache(('bot_id', bot_id))
                return bot_id

    def get_users(self):
        return self.slacker.users.list().body['members']
