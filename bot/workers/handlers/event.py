from bot.config import conf
from bot.utils.log_utils import log
from bot.utils.msg_utils import (
    chat_is_allowed,
    construct_event,
    event_handler,
    mentioned,
    user_is_owner,
)

from .dev import eval_handler, getlogs
from .fun import getmeme
from .gi import enka_handler
from .manage import pause_handler, restart_handler, update_handler


def handler(type_webhook: str, body: dict) -> None:
    if type_webhook == "incomingMessageReceived":
        event = construct_event(body)
        incoming_msg_handler(event)
    # elif type_webhook == "outgoingMessageReceived":
    # await outgoing_msg_handler(body)
    # elif type_webhook == "outgoingAPIMessageReceived":
    # await outgoing_amsg_handler(body)
    # elif type_webhook == "outgoingMessageStatus":
    # await outgoing_msg_status_handler(body)


def incoming_msg_handler(event):
    try:
        if not event.text:
            return
        if (event.ext_msg and not event.mentioned) and conf.IGNORE_UNMENTIONED:
            return
        if not (chat_is_allowed(event.chat.id) or user_is_owner(event.user.id)):
            return

        cp = conf.CMD_PREFIX
        command, arg = event.text.split(maxsplit=1) if len(event.text.split()) > 1 else (event.text, None)
        command = command.strip()
        if command.casefold() == f"{cp}enka":
            return event_handler(event, enka_handler, require_args=True)

        if command.casefold() == f"{cp}eval":
            return event_handler(event, eval_handler, require_args=True)
        if command.casefold() == f"{cp}logs":
            return event_handler(event, getlogs)

        if command.casefold() == f"{cp}meme":
            return event_handler(event, getmeme)

        if command.casefold() == f"{cp}pause":
            return event_handler(event, pause_handler)
        if command.casefold() == f"{cp}restart":
            return event_handler(event, restart_handler)
        if command.casefold() == f"{cp}update":
            return event_handler(event, update_handler)
    except Exception:
        log(Exception)
