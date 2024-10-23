from bot.config import _bot
from bot.utils.log_utils import logger
from bot.utils.msg_utils import user_is_owner
from bot.utils.os_utils import re_x, updater


async def restart_handler(event, args):
    """Restarts bot. (To avoid issues use /update instead.)"""
    if not user_is_owner(event.user.id):
        return
    try:
        rst = await event.reply("*Restarting Please Wait…*")
        message = str(rst.chat.id) + ":" + str(rst.id)
        await re_x("restart", message)
    except Exception:
        await event.reply("An Error Occurred")
        await logger(Exception)


async def update_handler(event, args):
    """Fetches latest update for bot"""
    try:
        if not user_is_owner(event.user.id):
            return
        upt_mess = "Updating…"
        reply = await event.reply(f"`{upt_mess}`")
        await updater(reply)
    except Exception:
        await logger(Exception)


async def pause_handler(event, args):
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
            return await event.reply(msg)
        if args.casefold() in ("on", "enable"):
            if _bot.paused:
                return await event.reply("Bot already paused.")
            _bot.paused = True
            return await event.reply("Bot has been paused.")
        elif args.casefold() in ("off", "disable"):
            if not _bot.paused:
                return await event.reply("Bot already unpaused.")
            _bot.paused = False
            return await event.reply("Bot has been unpaused.")
    except Exception:
        await logger(Exception)
