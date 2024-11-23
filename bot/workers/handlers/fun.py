import asyncio

from bot.utils.bot_utils import get_json
from bot.utils.log_utils import log

meme_list = []


def gen_meme(link):
    i = 1
    while True:
        result = asyncio.run(get_json(link))
        _id = result.get("ups")
        title = result.get("title")
        author = result.get("author")
        pl = result.get("postLink")
        if i > 20:
            raise Exception("Request Timeout!")
        i += 1
        if pl in meme_list:
            continue
        if len(meme_list) > 100:
            meme_list.clear()
        meme_list.append(pl)
        sb = result.get("subreddit")
        caption = f"*{title.strip()}*\n{pl}\n\nBy u/{author} in r/{sb}"
        url = result.get("url")
        filename = f"{_id}.{url.split('.')[-1]}"
        break
    return caption, url, filename


def getmeme(event, args):
    """
    Fetches a random meme from reddit
    Uses meme-api.com

    Arguments: 
    subreddit - custom subreddit
    """
    event.user.id
    link = "https://meme-api.com/gimme"
    try:
        if args:
            link += f"/{args}" if not arg.isdigit() else str()
        caption, url, filename = gen_meme(link)
        event.reply(caption, link=url, file_name=filename)
        # time.sleep(3)
    except Exception as e:
        log(Exception)
        return event.reply(f"*Error:*\n{e}")
