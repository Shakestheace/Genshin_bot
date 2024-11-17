import asyncio

from bot.utils.bot_utils import get_json
from bot.utils.log_utils import log

def getmeme(event, args):
    """
    Fetches a random meme from reddit 
    Uses meme-api.com
    Arguments: (Coming soon)
    -n number of memes to fetch
    -r specify subreddit 
    -nl hide post link
    """
    user = event.user.id
    link = "https://meme-api.com/gimme"
    try:
        if not args:
            result = asyncio.run(get_json(link))
            _id = result.get("ups")
            title = result.get("title")
            author = result.get("author")
            pl = result.get("postLink")
            sb = result.get("subreddit")
            caption = f"*{title}*\n{pl}\nBy u/{author} in r/{sb}"
            url = result.get("url")
            filename = f"{_id}.{url.split('.')[-1]}"
            event.reply(caption, link=url, file_name=filename)
    except Exception as e:
        log(Exception)
        return event.reply(f"*Error:*\n{e}")