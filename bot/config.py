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
import traceback

from decouple import config


class Config:
    def __init__(self):
        try:
            self.ALWAYS_DEPLOY_LATEST = config(
                "ALWAYS_DEPLOY_LATEST", default=False, cast=bool
            )
            self.ALLOWED_CHATS = config("ALLOWED_CHATS", default="")
            self.API_KEY = config("API_KEY", default=6, cast=int)
            self.API_HASH = config(
                "API_HASH", default="eb06d4abfb49dc3eeb1aeb98ae0f581e"
            )
            self.PH_NUMBER = config("PH_NUMBER", default="")

            self.CMD_PREFIX = config("CMD_PREFIX", default="")
            self.DATABASE_URL = config("DATABASE_URL", default=None)
            self.DBNAME = config("DBNAME", default="ENC")
            self.DYNO = config("DYNO", default=None)
            
            self.GROUP = config("LOG_GROUP", default=0, cast=int)
            self.OWNER = config("OWNER", default="",)
        except Exception:
            print("Environment vars Missing; or")
            print("Something went wrong:")
            print(traceback.format_exc())
            exit()


class Runtime_Config:
    def __init__(self):
        self.greenAPI = None
        self.offline = False
        self.paused = False
        self.version = None
        
        


conf = Config()
_bot = Runtime_Config()
