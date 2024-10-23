from bot.config import conf
from bot.utils.log_utils import logger
from bot.utils.msg_utils import chat_is_allowed, construct_event, mentioned

from .dev import eval_handler, getlogs
from .manage import pause_handler, restart_handler, update_handler


async def handler(type_webhook: str, body: dict) -> None:
    if type_webhook == "incomingMessageReceived":
        event = construct_event(body)
        await incoming_msg_handler(event)
    # elif type_webhook == "outgoingMessageReceived":
    # await outgoing_msg_handler(body)
    # elif type_webhook == "outgoingAPIMessageReceived":
    # await outgoing_amsg_handler(body)
    # elif type_webhook == "outgoingMessageStatus":
    # await outgoing_msg_status_handler(body)


async def incoming_msg_handler(event):
    try:
        print(event.text)
        if not event.text:
            return
        if not mentioned(event):
            return
        if not chat_is_allowed(event.chat.id):
            return
        cp = conf.CMD_PREFIX
        text = event.text.split(maxsplit=1)[1]
        command, arg = text.split(maxsplit=1)
        if command.casefold() == f"{cp}enka":
            return await event_handler(event, enka_handler, require_args=True)

        if command.casefold() == f"{cp}eval":
            return await event_handler(event, eval_handler, require_args=True)
        if command.casefold() == f"{cp}logs":
            return await event_handler(event, getlogs)

        if command.casefold() == f"{cp}pause":
            return await event_handler(event, pause_handler)
        if command.casefold() == f"{cp}restart":
            return await event_handler(event, restart_handler)
        if command.casefold() == f"{cp}update":
            return await event_handler(event, update_handler)
    except Exception:
        await logger(Exception)
