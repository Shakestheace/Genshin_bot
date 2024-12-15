import pickle

from pymongo import MongoClient

from bot import LOGS, bot, conf, os, sys, version_file
from bot.utils.bot_utils import create_api_token
from bot.utils.local_db_utils import load_enka_db, load_local_db
from bot.utils.os_utils import file_exists

LOGS.info("=" * 30)
LOGS.info(f"Python version: {sys.version.split()[0]}")

vmsg = f"Warning: {version_file} is missing!"
if file_exists(version_file):
    with open(version_file, "r") as file:
        ver = file.read().strip()
    vmsg = f"Bot version: {ver}"

LOGS.info(f"Branch: {bot.repo_branch or 'Unknown!'}")
LOGS.info(vmsg)

if os.path.isdir("/qiqi"):
    bot.docker_deployed = True
    LOGS.info("Docker: Yes")

LOGS.info("=" * 30)


if not os.path.isdir("enka/"):
    os.mkdir("enka/")

if file_exists(con_ind):
    bot.initialized_client = True

bot.gift_dict.update({"codes": [], "chats": []})


def load_db(_db, _key, var, var_type=None):
    queries = _db.find({"_id": conf.PH_NUMBER})
    raw = None
    for query in queries:
        raw = query.get(_key)

    if not raw:
        return
    out = pickle.loads(raw)
    if not out:
        return

    if var_type == "list":
        for item in out.split():
            if item in conf.OWNER.split():
                continue
            if item not in var:
                var.append(item)
    elif var_type == "dict":
        var.update(out)


if conf.DATABASE_URL:
    cluster = MongoClient(conf.DATABASE_URL)
    db = cluster[conf.DBNAME]
    rssdb = db["rss"]
    userdb = db["users"]
    miscdb = db["misc"]

    load_db(userdb, "banned_users", bot.banned, "list")
    load_db(miscdb, "gift", bot.gift_dict, "dict")
    load_db(rssdb, "rss", bot.rss_dict, "dict")


else:
    rssdb = userdb = miscdb = None

    load_local_db()

create_api_token()
load_enka_db()
