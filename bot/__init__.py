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


import logging
import sys
import traceback
from logging import DEBUG, INFO, basicConfig, getLogger, warning
from logging.handlers import RotatingFileHandler

from whatsapp_api_client_python import API

from .config import _bot, conf

log_file_name = "Logs.txt"
version_file = "version.txt"

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

if os.path.exists(version_file):
    with open(version_file, "r") as file:
        _bot.version = file.read().strip()

if sys.version_info < (3, 10):
    LOGS.critical("Please use Python 3.10+")
    exit(1)


try:
    _bot.greenAPI = API.GreenAPI(conf.API_KEY, conf.API_HASH)
except Exception:
    LOGS.info("Environment vars are missing or wrong! Kindly recheck.")
    LOGS.info("Bot is quiting...")
    LOGS.info(traceback.format_exc())
    exit(1)
