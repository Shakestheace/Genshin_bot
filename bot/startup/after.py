import signal

from bot import Message, asyncio, bot, con_ind, conf, jid, sys, version_file
from bot.fun.emojis import enmoji, enmoji2
from bot.fun.quips import enquip, enquip2
from bot.utils.gi_utils import enka_update
from bot.utils.local_db_utils import save_enka_db
from bot.utils.log_utils import logger
from bot.utils.msg_utils import send_presence
from bot.utils.os_utils import file_exists, force_exit, touch
from bot.utils.rss_utils import scheduler


async def update_enka_assets():
    if bot.enka_dict.get("Updated"):
        return
    await logger(e=("=" * 30))
    await logger(e="Updating enka assets…")
    await logger(e=("=" * 30))
    await enka_update()
    bot.enka_dict.update({"Updated": True})
    save_enka_db()


async def onrestart():
    try:
        if sys.argv[1] == "restart":
            msg = "*Restarted!*"
        elif sys.argv[1].startswith("update"):
            s = sys.argv[1].split()[1]
            if s == "True":
                with open(version_file, "r") as file:
                    v = file.read()
                msg = f"*Updated to >>>* {v}"
            else:
                msg = "*No major update found!*\n" f"Bot restarted! {enmoji()}"
        else:
            return
        chat_id, msg_id, server = map(str, sys.argv[2].split(":"))
        await bot.client.edit_message(
            jid.build_jid(chat_id, server), msg_id, Message(conversation=msg)
        )
    except Exception:
        await logger(Exception)


async def onstart():
    try:
        if bot.recently_initialized:
            await asyncio.sleep(10)
        for i in conf.OWNER.split():
            try:
                await bot.client.send_message(
                    jid.build_jid(i), f"*I'm {enquip()} {enmoji()}*"
                )
            except Exception:
                pass
    except BaseException:
        pass


async def on_termination():
    try:
        dead_msg = f"*I'm* {enquip2()} {enmoji2()}"
        for i in conf.OWNER.split():
            try:
                await bot.client.send_message(jid.build_jid(i), dead_msg)
            except Exception:
                pass
    except Exception:
        pass
    # More cleanup code?
    force_exit()
    # exit()


async def wait_on_client():
    while True:
        if (rep := await bot.client.is_logged_in):
            await logger(e=rep)
            if not file_exists(con_ind):
                touch(con_ind)
            break
        else:
            pass
        await asyncio.sleep(0.5)


async def on_startup():
    try:
        await update_enka_assets()
        scheduler.start()
        for signame in {"SIGINT", "SIGTERM", "SIGABRT"}:
            bot.loop.add_signal_handler(
                getattr(signal, signame),
                lambda: asyncio.create_task(on_termination()),
            )
        await wait_on_client()
        if len(sys.argv) == 3:
            await onrestart()
        else:
            await asyncio.sleep(1)
            await onstart()
        await send_presence()
        await asyncio.sleep(5)
        await send_presence(False)
        await logger(e="Bot has started.")
    except Exception:
        await logger(Exception)
