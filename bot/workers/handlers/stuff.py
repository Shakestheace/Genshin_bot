from clean_links.clean import clean_url
from urlextract import URLExtract

from bot.config import bot, conf
from bot.fun.quips import enquip
from bot.fun.stickers import ran_stick
from bot.utils.bot_utils import get_json
from bot.utils.log_utils import logger
from bot.utils.msg_utils import clean_reply, pm_is_allowed, user_is_allowed, user_is_owner

meme_list = []


async def gen_meme(link, pm=False):
    i = 1
    while True:
        result = await get_json(link)
        _id = result.get("ups")
        title = result.get("title")
        if not title:
            return None, None, None, None
        author = result.get("author")
        pl = result.get("postLink")
        if i > 100:
            raise Exception("Request Timeout!")
        i += 1
        if pl in meme_list:
            continue
        if len(meme_list) > 10000:
            meme_list.clear()
        nsfw = result.get("nsfw")
        if bot.block_nsfw and nsfw and not pm:
            return None, None, None, True
        meme_list.append(pl)
        sb = result.get("subreddit")
        nsfw_text = "*🔞 NSFW*\n"
        caption = f"{nsfw_text if nsfw else str()}*{title.strip()}*\n{pl}\n\nBy u/{author} in r/{sb}"
        url = result.get("url")
        filename = f"{_id}.{url.split('.')[-1]}"
        nsfw = False if pm else nsfw
        break
    return caption, url, filename, nsfw


async def getmeme(event, args, client):
    """
    Fetches a random meme from reddit
    Uses meme-api.com

    Arguments:
    subreddit - custom subreddit
    """
    user = event.from_user.id
    if not user_is_owner(user):
        if not pm_is_allowed(event):
            return
        if not user_is_allowed(user):
            return
    link = "https://meme-api.com/gimme"
    try:
        if args:
            link += f"/{args}" if not args.isdigit() else str()
        caption, url, filename, nsfw = await gen_meme(link, not (event.chat.is_group))
        if not url:
            if nsfw:
                return await event.reply("*NSFW is blocked!*")
            return await event.reply("*Request Failed!*")
        await event.reply_photo(
            caption=caption,
            photo=url,
            viewonce=nsfw,
        )
    except Exception as e:
        await logger(Exception)
        return await event.reply(f"*Error:*\n{e}")


async def getcmds(event, args, client):
    """
    Get list of commands

    Arguments:
        None
    """
    user = event.from_user.id
    if not user_is_owner(user):
        if not pm_is_allowed(event):
            return
        if not user_is_allowed(user):
            return
    try:
        pre = conf.CMD_PREFIX
        msg = f"""{pre}start - *Hi!*
{pre}enka - *Fetch enka cards*
{pre}weapon - *Fetch weapon details*
{pre}meme - *Get a random meme*
{pre}codes - *Get lastest giftcodes*
{pre}sanitize - *Sanitize link or message*
{pre}bash - *[Dev.] Run bash commands*
{pre}eval - *[Dev.] Evaluate python commands*
{pre}rss - *[Owner] Setup bot to auto post RSS feeds*
{pre}update - *[Owner] Update & restarts bot*
{pre}restart - *[Owner] Restarts bot*
{pre}pause - *[Owner] Pauses bot*"""
        await event.reply(msg)
    except Exception as e:
        await logger(Exception)
        return await event.reply(f"*Error:*\n{e}")


async def hello(event, args, client):
    try:
        await event.reply("Hi!")
    except Exception:
        await logger(Exception)


async def sticker_reply(event, args, client):
    """
    Sends a random sticker upon being tagged
    """
    try:
        if event.type != "text":
            return
        if not event.text.startswith("@"):
            return
        me = await bot.client.get_me()
        if not event.text.startswith("@" + me.JID.User):
            return
        random_sticker = ran_stick()
        await event.reply_sticker(
            random_sticker, quote=True, name=enquip(), packname=me.PushName
        )
    except Exception:
        await logger(Exception)


async def sanitize_url(event, args, client):
    """
    Checks and sanitizes all links in replied message

    Can also receive a link as argument
    """
    status_msg = None
    try:
        if not (event.quoted_text or args):
            return event.reply(sanitize_url.__doc__)
        status_msg = await event.reply("Please wait…")
        extractor = URLExtract()
        if event.quoted_text:
            msg = event.quoted_text
            urls = extractor.find_urls(msg)
            if not urls:
                return await event.reply(
                    f"*No link found in @{event.reply_to_message.from_user.id}'s message to sanitize*"
                )
            new_msg = msg
            sanitized_links = []
            for url in urls:
                sanitized_links.append(clean_url(url))
            for a, b in zip(urls, sanitized_links):
                new_msg = new_msg.replace(a, b)
            return await clean_reply(event,event.reply_to_message, "reply", new_msg)
        urls = extractor.find_urls(args)
        if not urls:
            return await event.reply(f"*No link found in your message to sanitize*")
        msg = "*Sanitized link(s):*"
        for url in urls:
            msg += f"\n\n{url}"
        return await clean_reply(event, event.reply_to_message, "reply", msg)
    except Exception:
        await logger(Exception)
    finally:
        if status_msg:
            await status_msg.delete()
