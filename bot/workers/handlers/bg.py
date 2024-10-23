import asyncio
import sys
import threading

from bot import _bot
from bot.utils.bot_utils import sync_to_async
from bot.utils.log_utils import log, logger

from .event import handler


def bg_handler(*args, **kwargs):
    try:
        t = threading.Thread(
            target=lambda: asyncio.run(bg_task(handler, *args, **kwargs))
        )
        t.start()
    except Exception:
        log(Exception, critical=True)


async def bg_task(func, *args, **kwargs):
    try:
        asyncio.create_task(func(*args, **kwargs))
    except Exception:
        await logger(Exception, critical=True)


async def onrestart():
    if len(sys.argv) == 3:
        asyncio.create_task(restart_handler())


async def restart_handler():
    try:
        if sys.argv[1] == "restart":
            msg = "*Restarted!* "
        elif sys.argv[1].startswith("update"):
            s = sys.argv[1].split()[1]
            if s == "True" and _bot.version:
                msg = f"*Updated to >>>* `{_bot.version}`"
            else:
                msg = "*No major update found!*\n" f"`Bot restarted!`"
        else:
            return
        chat_id, msg_id = map(str, sys.argv[2].split(":"))
        _bot.greenAPI.sending.sendMessage(chat_id, msg, msg_id)
    except Exception:
        await logger(Exception)
