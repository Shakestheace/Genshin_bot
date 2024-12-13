import argparse
import asyncio
import copy
import os
import re
from functools import partial

from bs4 import BeautifulSoup

from bot import (
    Message,
    MessageEv,
    NewAClient,
    base_msg,
    base_msg_info,
    base_msg_source,
    jid,
)
from bot.config import bot, conf
from bot.others.exceptions import ArgumentParserError

from .bot_utils import post_to_tgph
from .log_utils import logger


class Event:
    def __init__(self):
        self.client = bot.client
        self.constructed = False

    def __str__(self):
        return self.text

    class User:
        def __init__(self):
            self.name = None

        def construct(self, message: MessageEv):
            self.jid = message.Info.MessageSource.Sender
            self.id = self.jid.User
            self.is_empty = message.Info.MessageSource.Sender.IsEmpty
            self.name = message.Info.Pushname

    class Chat:
        def __init__(self):
            self.name = None

        def construct(self, message: MessageEv):
            self.jid = message.Info.MessageSource.Chat
            self.id = self.jid.User
            self.is_empty = message.Info.MessageSource.Sender.IsEmpty
            self.is_group = message.Info.MessageSource.IsGroup

    def construct(self, message: MessageEv, add_replied: bool = True):
        self.chat = self.Chat()
        self.chat.construct(message)
        self.from_user = self.User()
        self.from_user.construct(message)
        self.message = message

        # To do support other message types
        self.id = message.Info.ID
        self.type = message.Info.Type
        self.media_type = message.Info.MediaType
        self.ext_msg = message.Message.extendedTextMessage
        self.text_msg = message.Message.conversation
        self.short_text = self.text_msg
        self.text = self.ext_msg.text
        # mention_str = f"@{(self.w_id.split('@'))[0]}"
        # self.mentioned = self.text.startswith(mention_str) if self.text else False
        # if self.mentioned:
        #    self.text = (self.text.split(maxsplit=1)[1]).strip()
        self.text = self.text or self.short_text
        # To do expand quoted; has members [stanzaID, participant,
        # quotedMessage.conversation]
        self.quoted = self.ext_msg.contextInfo if add_replied else None
        self.reply_to_message = self.get_quoted_msg()
        self.outgoing = message.Info.MessageSource.IsFromMe
        self.is_status = message.Info.MessageSource.Chat.User.casefold() == "status"
        self.constructed = True
        return self

    async def delete(self):
        await self.client.revoke_message(self.chat.jid, self.from_user.jid, self.id)
        return None

    async def edit(self, text: str):
        msg = Message(conversation=text)
        response = await self.client.edit_message(self.chat.jid, self.id, msg)
        msg = self.gen_new_msg(response.ID)
        return construct_event(msg)

    async def reply(
        self,
        text: str = None,
        file: str | bytes = None,
        file_name: str = None,
        image: str = None,
        quote: bool = True,
        link_preview: bool = True,
        reply_privately: bool = False,
    ):
        if not self.constructed:
            return
        if file:
            return await self.reply_document(file, file_name, text, quote)
        if image and file_name:
            return await self.reply_photo(image, text, quote)
        if not text:
            raise Exception("Specify a text to reply with.")
        # msg_id = self.id if quote else None

        response = await self.client.reply_message(
            text,
            self.message,
            link_preview=link_preview,
            reply_privately=reply_privately,
        )
        # self.id = response.ID
        # self.text = text
        # new_jid = jid.build_jid(conf.PHNUMBER)
        # self.user.jid = new_jid
        # self.user.id = new_jid.User

        # self.user.name = None
        msg = self.gen_new_msg(response.ID)
        return construct_event(msg)

    async def reply_document(
        self,
        document: str | bytes,
        file_name: str = None,
        caption: str = None,
        quote: bool = True,
    ):
        quoted = self.message if quote else None
        _, file_name = (
            os.path.split(document)
            if not file_name and isinstance(document, str)
            else (None, file_name)
        )
        response = await self.client.send_document(
            self.chat.jid, document, caption, filename=file_name, quoted=quoted
        )
        msg = self.gen_new_msg(response.ID)
        return construct_event(msg)

    async def reply_photo(
        self,
        photo: str | bytes,
        caption: str = None,
        quote: bool = True,
        viewonce: bool = False,
    ):
        quoted = self.message if quote else None
        response = await self.client.send_image(
            self.chat.jid, photo, caption, quoted=quoted, viewonce=viewonce
        )
        msg = self.gen_new_msg(response.ID)
        return construct_event(msg)

    async def upload_file(self, file: bytes):
        response = await self.client.upload(file)
        msg = self.gen_new_msg(response.ID)
        return construct_event(msg)

    def gen_new_msg(self, msg_id: str, user_id: str = None):
        msg = copy.deepcopy(self.message)
        msg.Info.ID = msg_id
        msg.Info.MessageSource.Sender.User = user_id or conf.PH_NUMBER
        return msg

    def get_quoted_msg(self):
        if not (self.quoted and self.quoted.stanzaID):
            return
        msg = self.gen_new_msg(
            self.quoted.stanzaID, (self.quoted.participant.split("@"))[0]
        )
        return construct_event(msg, False)


def user_is_allowed(user: str | int):
    user = str(user)
    return user not in bot.banned


def user_is_owner(user: str | int):
    user = str(user)
    return user in conf.OWNER


def user_is_dev(user: str):
    user = int(user)
    return user == conf.DEV


def pm_is_allowed(event: Event):
    if not event.chat.is_group:
        return not bot.ignore_pm
    return True


function_dict = {None: []}


def register(key: str | None = None):
    def dec(fn):
        nonlocal key
        if not key:
            function_dict[key].append(fn)
        else:
            key = conf.CMD_PREFIX + key
            function_dict.update({key: fn})

    return dec


bot.register = register


async def on_message(client: NewAClient, message: MessageEv):
    event = construct_event(message)
    if event.type == "text":
        command, args = (
            event.text.split(maxsplit=1)
            if len(event.text.split()) > 1
            else (event.text, None)
        )
        func = function_dict.get(command)
        if func:
            await func(client, event)
    for func in function_dict[None]:
        await func(client, event)


def construct_event(message: MessageEv, add_replied=True):
    msg = Event()
    return msg.construct(message, add_replied=add_replied)


def construct_message(chat_id, user_id, msg_id, text, server="s.whatsapp.net"):
    return base_msg(
        Message=Message(conversation=text),
        Info=base_msg_info(
            ID=msg_id,
            MessageSource=base_msg_source(
                Chat=jid.build_jid(chat_id, server),
                Sender=jid.build_jid(user_id),
            ),
        ),
    )


# def mentioned(event):
# return event.text.startswith(f"@{(event.w_id.split('@'))[0]}")


def sanitize_text(text: str) -> str:
    if not text:
        return text
    text = BeautifulSoup(text, "html.parser").text
    return (text[:900] + "…") if len(text) > 900 else text


async def parse_and_send_rss(data: dict, chat_ids: list = None):
    try:
        author = data.get("author")
        chats = chat_ids or conf.RSS_CHAT.split()
        pic = data.get("pic")
        content = data.get("content")
        summary = sanitize_text(data.get("summary"))
        tgh_link = str()
        title = data.get("title")
        url = data.get("link")
        # auth_text = f" by {author}" if author else str()
        caption = f"*{title}*"
        caption += f"\n`{summary or str()}`"
        if content:
            if len(content) > 65536:
                content = (
                    content[:65430]
                    + "<strong>...<strong><br><br><strong>(TRUNCATED DUE TO CONTENT EXCEEDING MAX LENGTH)<strong>"
                )
            tgh_link = (await post_to_tgph(title, content, author, url))["url"]
            caption += f"\n\n*Telegraph:* {tgh_link}\n*Hoyolab:* {url}"
        expanded_chat = []
        for chat in chats:
            (
                expanded_chat.append(chat)
                if chat
                else expanded_chat.extend(conf.RSS_CHAT.split())
            )
        for chat in expanded_chat:
            top_chat = chat.split(":")
            chat, server = (
                map(str, top_chat)
                if len(top_chat) > 1
                else (str(top_chat[0]), "s.whatsapp.net")
            )
            await send_rss(caption, chat, pic, server)
            await asyncio.sleep(5)
    except Exception:
        await logger(Exception)


async def send_rss(caption, chat, pic, server):
    try:
        len_pic = len(pic)
        if len_pic > 1:
            i = 0
            rep = await bot.client.send_image(
                jid.build_jid(chat, server=server),
                pic[0],
                caption,
            )
            message = construct_message(
                chat, conf.PH_NUMBER, rep.ID, "image", server=server
            )
            msg = construct_event(message)
            for img in pic[1:]:
                i += 1
                caption = f"*({i} of {len_pic - 1})*"
                msg = await msg.reply_photo(img, caption, quote=True)
        elif pic:
            await bot.client.send_image(
                jid.build_jid(chat, server),
                pic[0],
                caption,
            )
        else:
            await bot.client.send_message(
                jid.build_jid(chat, server),
                caption,
            )
    except Exception:
        await logger(Exception)


async def clean_reply(event, reply, func, *args, **kwargs):
    clas = reply if reply else event
    func = getattr(clas, func)
    pfunc = partial(func, *args, **kwargs)
    return await pfunc()


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


async def event_handler(
    event,
    function,
    client=None,
    require_args=False,
    disable_help=False,
    split_args=" ",
    default_args: str = False,
    use_default_args=False,
):
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
        return await event.reply(f"{function.__doc__}")
    await function(event, args, client)
