from bot.utils.os_utils import re_x, s_remove

from . import (
    LOGS,
    ConnectedEv,
    LoggedOutEv,
    MessageEv,
    NewAClient,
    asyncio,
    bot,
    con_ind,
    conf,
    time,
    traceback,
)
from .startup.after import on_startup
from .utils.msg_utils import Event, event_handler, on_message
from .utils.os_utils import re_x, s_remove
from .workers.handlers.dev import bash, eval_message, get_logs
from .workers.handlers.gi import enka_handler, get_events, getgiftcodes, weapon_handler
from .workers.handlers.manage import (
    pause_handler,
    restart_handler,
    rss_handler,
    update_handler,
)
from .workers.handlers.stuff import (
    getcmds,
    getmeme,
    hello,
    sanitize_url,
    sticker_reply,
    stickerize_image,
)


@bot.client.event(ConnectedEv)
async def on_connected(_: NewAClient, __: ConnectedEv):
    LOGS.info("Bot has started.")


@bot.client.event(LoggedOutEv)
async def on_logout(_: NewAClient, __: LoggedOutEv):
    s_remove(con_ind)
    LOGS.info("Bot has been logged out.")
    LOGS.info("Restarting…")
    time.sleep(10)
    re_x()


@bot.register("start")
async def _(client: NewAClient, message: Event):
    await event_handler(message, hello)


@bot.register("pause")
async def _(client: NewAClient, message: Event):
    await event_handler(message, pause_handler)


@bot.register("logs")
async def _(client: NewAClient, message: Event):
    await event_handler(message, get_logs)


@bot.register("eval")
async def _(client: NewAClient, message: Event):
    await event_handler(message, eval_message, require_args=True)


@bot.register("bash")
async def _(client: NewAClient, message: Event):
    await event_handler(message, bash, require_args=True)


@bot.register("enka")
async def _(client: NewAClient, message: Event):
    await event_handler(message, enka_handler, require_args=True)


@bot.register("weapon")
async def _(client: NewAClient, message: Event):
    await event_handler(message, weapon_handler, require_args=True)


@bot.register("meme")
async def _(client: NewAClient, message: Event):
    await event_handler(message, getmeme)


@bot.register("cmds")
async def _(client: NewAClient, message: Event):
    await event_handler(message, getcmds)


@bot.register("codes")
async def _(client: NewAClient, message: Event):
    await event_handler(message, getgiftcodes)


@bot.register("events")
async def _(client: NewAClient, message: Event):
    await event_handler(message, get_events)


@bot.register("sanitize")
async def _(client: NewAClient, message: Event):
    await event_handler(message, sanitize_url)


@bot.register("sticker")
async def _(client: NewAClient, message: Event):
    await event_handler(message, stickerize_image)


@bot.register("rss")
async def _(client: NewAClient, message: Event):
    await event_handler(message, rss_handler, require_args=True)


@bot.register("update")
async def _(client: NewAClient, message: Event):
    await event_handler(message, update_handler)


@bot.register("restart")
async def _(client: NewAClient, message: Event):
    await event_handler(message, restart_handler)


@bot.register(None)
async def _(client: NewAClient, message: Event):
    await sticker_reply(message, None, client)


@bot.client.event(MessageEv)
async def _(client: NewAClient, message: MessageEv):
    await on_message(client, message)


########### Start ############

try:
    loop = asyncio.get_event_loop()
    bot.loop = loop
    loop.create_task(on_startup())
    if not bot.initialized_client:
        loop.run_until_complete(
            bot.client.PairPhone(conf.PH_NUMBER, show_push_notification=True)
        )
    else:
        loop.run_until_complete(bot.client.connect())
except Exception:
    LOGS.critical(traceback.format_exc())
    LOGS.critical("Cannot recover from error, exiting…")
    exit()
