import aiohttp
from aiohttp_retry import RandomRetry, RetryClient
from encard import encard, update_namecard
from enkacard import enc_error, encbanner

from .log_utils import logger

uri = "https://genshin-db-api.vercel.app/api/v5/{}?query={}&dumpResult=true"
uri2 = (
    "https://genshin-db-api.vercel.app/api/v5/stats?folder={}&query={}&dumpResult=true"
)


async def get_gi_info(
    folder="characters", query="qiqi", direct=False, stats=False, get=None
):
    url = uri.format(folder, query) if not stats else uri2.format(folder, query)
    if get:
        direct = True
        url = get
    field = "stats" if stats else "result"
    retry_options = RandomRetry(attempts=10)
    client_session = aiohttp.ClientSession()
    retry_requests = RetryClient(client_session)
    async with retry_requests.get(url, retry_options=retry_options) as result:
        if direct:
            info = await result.json()
        else:
            info = (await result.json()).get(field)
    await client_session.close()
    return info


async def async_dl(url):
    retry_options = RandomRetry(attempts=10)
    client_session = aiohttp.ClientSession()
    retry_requests = RetryClient(client_session)
    async with retry_requests.get(url, retry_options=retry_options) as result:
        assert result.status == 200
        raw = await result.content.read()
    await client_session.close()
    return raw


async def enka_update():
    await encbanner.update()
    await update_namecard.update()


async def get_enka_profile(uid, card=False, template=1):
    error = None
    result = None
    try:
        async with encbanner.ENC(uid=uid) as encard:
            result = await encard.profile(card=card, teamplate=template)
    except enc_error.ENCardError as e:
        error = e
    except Exception as e:
        error = e
        await logger(Exception)
    finally:
        return result, error


async def get_enka_card(uid, char_id, akasha=True, huid=False, template=1):
    error = False
    result = None
    try:
        async with encbanner.ENC(
            uid=uid, character_id=str(char_id), hide_uid=huid
        ) as encard:
            result = await encard.creat(akasha=akasha, template=template)
    except enc_error.ENCardError as e:
        error = True
        result = e
    except Exception as e:
        error = True
        result = e
        await logger(Exception)
    finally:
        return result, error


async def get_enka_profile2(uid, huid=False):
    error = result = None
    try:
        async with encard.ENCard(lang="en", hide=huid) as enc:
            result = await enc.create_profile(uid)
    except Exception as e:
        error = True
        result = e
        await logger(Exception)
    finally:
        return result, error


async def get_enka_card2(uid, char_id, huid=False):
    error = result = None
    try:
        async with encard.ENCard(
            lang="en", character_id=str(char_id), hide=huid
        ) as enc:
            result = await enc.create_cards(uid)
    except Exception as e:
        error = True
        result = e
        await logger(Exception)
    finally:
        return result, error
