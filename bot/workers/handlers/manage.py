import time

from bot.config import _bot
from bot.utils.log_utils import log
from bot.utils.msg_utils import user_is_owner
from bot.utils.os_utils import re_x, updater


def restart_handler(event, args):
    """Restarts bot. (To avoid issues use /update instead.)"""
    if not user_is_owner(event.user.id):
        return
    try:
        rst = event.reply("*Restarting Please Wait…*")
        message = str(rst.chat.id) + ":" + str(rst.id)
        time.sleep(5)
        re_x("restart", message)
    except Exception:
        event.reply("An Error Occurred")
        log(Exception)


def update_handler(event, args):
    """Fetches latest update for bot"""
    try:
        if not user_is_owner(event.user.id):
            return
        upt_mess = "Updating…"
        reply = event.reply(f"`{upt_mess}`")
        time.sleep(5)
        updater(reply)
    except Exception:
        log(Exception)


def pause_handler(event, args):
    """
    Pauses bot/ bot ignores Non-owner queries
    Arguments:
        -: on/enable <str> pauses bot
        -: off/disable <str> unpauses bot
        -: no argument <str> checks state
    """
    try:
        if not user_is_owner(event.user.id):
            return
        if not args:
            msg = f"Bot is currently {'paused' if _bot.paused else 'unpaused'}."
            return event.reply(msg)
        if args.casefold() in ("on", "enable"):
            if _bot.paused:
                return event.reply("Bot already paused.")
            _bot.paused = True
            return event.reply("Bot has been paused.")
        elif args.casefold() in ("off", "disable"):
            if not _bot.paused:
                return event.reply("Bot already unpaused.")
            _bot.paused = False
            return event.reply("Bot has been unpaused.")
    except Exception:
        log(Exception)
