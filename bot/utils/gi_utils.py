import aiohttp
from enkacard import encbanner
from enkacard import enc_error
import asyncio
import os
import traceback

from .log_utils import log, logger


uri = "https://genshin-db-api.vercel.app/api/v5/{}?query={}&dumpResult=true"
async def get_gi_info(folder="characters", query=gi_query, direct=False):
    url = uri.format(folder, query)
    async with aiohttp.ClientSession() as requests:
        result = await requests.get(url)
        if direct:
            return await result.json()
        info = await result.json().get("result")
    return info

async def enka_update():
    await encbanner.update()

async def get_enka_profile(uid, card=False, template=1):
    error = False
    try:
        async with encbanner.ENC(uid=uid) as encard:
            result = await encard.profile(card=card, teamplate=template)
    except enc_error.ENCardError as e:
        error = True
        result = e
    except Exception as e:
        error = True
        result = e
        await logger (Exception)
    finally return result, error

async def get_enka_card(uid, char_id, akasha=True, huid=False, template=1):
    error=False 
    try:
        async with encbanner.ENC(uid=uid, character_id=str(char_id), hide_uid=huid) as encard:
            result = await encard.creat(akasha=akasha, template=template)
    except enc_error.ENCardError as e:
        error = True
        result = e
    except Exception as e:
        error = True
        result = e
        await logger (Exception)
    finally return result, error
