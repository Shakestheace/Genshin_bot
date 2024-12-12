#    This file is part of the Genshin_bot distribution.
#    Copyright (c) 2024 Nubuki-all
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
# License can be found in <
# https://github.com/Nubuki-all/Genshin_bot/blob/WA/License> .


import asyncio
import logging
import os
import re
import shlex
import subprocess
import sys
import time
import traceback
from logging import DEBUG, INFO, basicConfig, getLogger, warning
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import urlparse

from html_telegraph_poster import TelegraphPoster
from html_telegraph_poster import errors as telegraph_errors
from neonize.aioze.client import NewAClient
from neonize.events import (
    CallOfferEv,
    ConnectedEv,
    MessageEv,
    PairStatusEv,
    ReceiptEv,
    event,
)
from neonize.proto.waE2E.WAWebProtobufsE2E_pb2 import (
    ContextInfo,
    ExtendedTextMessage,
    Message,
)
from neonize.utils import jid, log

from .config import bot, conf

local_rdb = ".local_rssdb.pkl"
local_budb = ".banned_users.pkl"
local_enkadb = ".local_enkadb.pkl"
log_file_name = "logs.txt"
rss_dict_lock = asyncio.Lock()
uptime = time.time()
version_file = "version.txt"
wa_db = "db.sqlite3"

if os.path.exists(log_file_name):
    with open(log_file_name, "r+") as f_d:
        f_d.truncate(0)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(log_file_name, maxBytes=2097152000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("urllib3").setLevel(logging.INFO)
LOGS = logging.getLogger(__name__)

no_verbose = [
    "apscheduler.executors.default",
]
if not conf.DEBUG:
    log.setLevel(logging.INFO)
    for item in no_verbose:
        logging.getLogger(item).setLevel(logging.WARNING)

bot.repo_branch = (
    subprocess.check_output(["git rev-parse --abbrev-ref HEAD"], shell=True)
    .decode()
    .strip()
    if os.path.exists(".git")
    else None
)
if os.path.exists(version_file):
    with open(version_file, "r") as file:
        bot.version = file.read().strip()

if sys.version_info < (3, 10):
    LOGS.critical("Please use Python 3.10+")
    exit(1)

LOGS.info("Starting...")

bot.ignore_pm = conf.IGNORE_PM
bot.tgp_client = TelegraphPoster(use_api=True, telegraph_api_url=conf.TELEGRAPH_API)

bot.client = NewAClient(wa_db)
