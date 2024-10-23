#    This file is part of the Encoder distribution.
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
# License can be found in
# <https://github.com/Nubuki-all/Genshin_bot/blob/main/License> .


from bot.workers.handlers.bg import bg_handler, onrestart

from . import LOGS, _bot, traceback

LOGS.info(f"Bot version: {_bot.version}")
LOGS.info("Starting...")


######## Connect ########


def main():
    try:

        onrestart()
        _bot.greenAPI.webhooks_.startReceivingNotifications(bg_handler)
    except Exception:
        LOGS.info(traceback.format_exc())


########### Start ############

try:
    if __name__ == "__main__":
        main()
except Exception:
    LOGS.critical(traceback.format_exc())
    exit()
