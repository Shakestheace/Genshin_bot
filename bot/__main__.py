#    This file is part of the Encoder distribution.
#    Copyright (c) 2023 Danish_00, Nubuki-all
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
# <https://github.com/Nubuki-all/Enc/blob/main/License> .

import asyncio

from bot.workers.handlers.bg import bg_handler, onrestart

from . import LOGS, _bot, traceback

LOGS.info(f"Bot version: {_bot.version}")
LOGS.info("Starting...")


######## Connect ########


async def main():
    try:

        _bot.greenAPI.webhooks.startReceivingNotifications(bg_handler)
    except Exception:
        LOGS.info(traceback.format_exc())


########### Start ############
bot = asyncio.new_event_loop()
try:
    bot.run_until_complete(onrestart())
    bot.run_until_complete(main())
    bot.run_forever()
except Exception:
    LOGS.critical(traceback.format_exc())
    exit()
