import argparse
import re
import shutil
import urllib.request

from bot.config import _bot, conf
from bot.others.exceptions import ArgumentParserError

from .os_utils import s_remove

# from .log_utils import log, logger


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


def line_split(line):
    return [t.strip("\"'") for t in re.findall(r'[^\s"]+|"[^"]*"', line)]


def get_args(*args, to_parse: str, get_unknown=False):
    parser = ThrowingArgumentParser(
        description="parse command flags", exit_on_error=False, add_help=False
    )
    for arg in args:
        if isinstance(arg, list):
            parser.add_argument(arg[0], action=arg[1], required=False)
        else:
            parser.add_argument(arg, type=str, required=False)
    flag, unknowns = parser.parse_known_args(line_split(to_parse))
    if get_unknown:
        unknown = " ".join(map(str, unknowns))
        return flag, unknown
    return flag


class Message:
    def __init__(self):
        self.client = _bot.greenAPI
        self.constructed = False

    def __str__(self):
        return self.text

    class User:
        def __init__(self):
            self.id = None
            self.name = None

        def construct(self, body):
            self.id = body.get("senderData").get("sender")
            self.name = body.get("senderData").get("senderName")

    class Chat:
        def __init__(self):
            self.id = None
            self.name = None

        def construct(self, body):
            self.id = body.get("senderData").get("chatId")
            self.name = body.get("senderData").get("chatName")

    def construct(self, body):
        self.chat = self.Chat()
        self.chat.construct(body)
        self.user = self.User()
        self.user.construct(body)

        # To do support other message types
        self.id = body.get("idMessage")
        self.type = body.get("messageData").get("typeMessage")
        self.ext_msg = body.get("messageData").get("extendedTextMessageData")
        self.text_msg = body.get("messageData").get("textMessageData")
        self.short_text = self.text_msg.get("textMessage") if self.text_msg else None
        self.text = self.ext_msg.get("text") if self.ext_msg else None
        self.w_id = body.get("instanceData").get("wid")
        mention_str = f"@{(self.w_id.split('@'))[0]}"
        self.mentioned = self.text.startswith(mention_str) if self.text else False
        if self.mentioned:
            self.text = (self.text.split(maxsplit=1)[1]).strip()
        self.text = self.text or self.short_text
        # To do expand quoted
        self.quoted = body.get("messageData").get("quotedMessage")
        self.constructed = True
        return self

    def reply(self, text=None, file=None, file_name=None, link=None, quote=True):
        if not self.constructed:
            raise Exception("Method not ready.")
        if file and file_name:
            return self.reply_file(file, file_name, text, quote)
        if link and file_name:
            return self.reply_link(link, file_name, text, quote)
        if not text:
            raise Exception("Specify a text to reply with.")
        msg_id = self.id if quote else None
        print("here.")
        # response = await sync_to_async(
        #    self.client.sending.sendMessage, self.chat.id, text, msg_id
        # )
        response = self.client.sending.sendMessage(self.chat.id, text, msg_id)
        print(response.data)
        self.id = response.data.get("idMessage")
        self.text = text
        self.user.id = self.w_id
        self.user.name = None
        return self

    def reply_file(self, file, file_name, caption=None, quote=True):
        msg_id = self.id if quote else None
        # response = await sync_to_async(
        #    self.client.sending.sendFileByUpload,
        #    self.chat.id,
        #    file,
        #    file_name,
        #    caption,
        #    msg_id,
        # )
        response = self.client.sending.sendFileByUpload(
            self.chat.id, file, file_name, caption, msg_id
        )
        self.id = response.data.get("idMessage")
        self.text = caption
        self.user.id = self.w_id
        self.user.name = None
        return self

    def reply_link(self, link, file_name, caption=None, quote=True):
        msg_id = self.id if quote else None

        with urllib.request.urlopen(link) as response, open(
            file_name, "wb"
        ) as out_file:
            shutil.copyfileobj(response, out_file)
        link = self.client.sending.uploadFile(file_name)
        response = self.client.sending.sendFileByUrl(
            self.chat.id, link, file_name, caption, msg_id
        )
        s_remove(file_name)
        self.id = response.data.get("idMessage")
        self.text = caption
        self.user.id = self.w_id
        self.user.name = None
        return self


def construct_event(body):
    msg = Message()
    return msg.construct(body)


def mentioned(event):
    return event.text.startswith(f"@{(event.w_id.split('@'))[0]}")


def chat_is_allowed(user):
    return user in conf.ALLOWED_CHATS if conf.ALLOWED_CHATS else True


def user_is_owner(user):
    return user.split("@")[0] in conf.OWNER if conf.OWNER else False


def event_handler(
    event,
    function,
    require_args=False,
    disable_help=False,
    split_args=" ",
    default_args: str = False,
    use_default_args=False,
):
    # etext = event.text or event.short_text
    args = (
        event.text.split(split_args, maxsplit=1)[1].strip()
        if len(event.text.split()) > 1
        else None
    )
    args = default_args if use_default_args and default_args is not False else args
    help_tuple = ("--help", "-h")
    if (
        (require_args and not args)
        or (args and args.casefold() in help_tuple)
        or (require_args and not (default_args or default_args is False))
        or (default_args in help_tuple)
    ):
        if disable_help:
            return
        return event.reply(f"```{function.__doc__}```")
    function(event, args)
