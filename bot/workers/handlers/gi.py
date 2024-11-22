import asyncio
import time

from bot.utils.gi_utils import enka_update, get_enka_card, get_enka_profile, get_gi_info
from bot.utils.log_utils import log
from bot.utils.msg_utils import get_args
from bot.utils.os_utils import s_remove


def enka_handler(event, args):
    """
    Get a players's character build card from enka
    Requires character build for the specified uid to be public

    Arguments:
    uid: {genshin player uid} (Required)
    -c or --card {character name}: use quotes if the name has spaces eg:- "Hu tao"; Also supports lookups
    -cs or --cards {characters} same as -c but for multiple characters; delimited by commas
    -t <int> {template}: card generation template; currently only two templates exist; default 1
    Flags:
    -v2: Get cards in new template 
    -d or --dump: Dump all character build from the given uid
    -p or --profile: To get player card instead
    --hide_uid: Hide uid in card
    --no_top: Remove akasha ranking from card
    --update: update library

    Examples:
    123454697855 -c "Hu tao" -t 2 --hide_uid
        - retrieves the current build for Hu tao from the given uid with uid hidden while using the second template
    123456789 -p -t 2
        - retrieves profile card using the second template for the given uid
    12345678900 -c xq
        - retrieves the current build for whatever matches the character name provided; in this case Xingqui
    """
    error = None
    try:
        arg, args = get_args(
            ["--hide_uid", "store_true"],
            ["--no_top", "store_false"],
            ["--update", "store_true"],
            "-c",
            "-cs",
            "--card",
            "--cards",
            ["-d", "store_true"],
            ["--dump", "store_true"],
            ["-p", "store_true"],
            ["--profile", "store_true"],
            ["-v2", "store_true"],
            "-t",
            to_parse=args,
            get_unknown=True,
        )
        card = arg.c or arg.card
        cards = arg.cs or arg.cards
        dump = arg.d or arg.dump
        prof = arg.p or arg.profile
        akasha = arg.no_top
        if arg.update:
            enka_update()
            if not (card or cards or dump or prof):
                return event.reply("Updated enka assets.")
        if not (card or cards or dump or prof):
            return event.reply(f"```{enka_handler.__doc__}```")
        if arg.t not in ("1", "2"):
            arg.t = 1
        profile, error = asyncio.run(get_enka_profile(args))
        if error:
            return
        if prof:
            cprofile, error = asyncio.run(
                get_enka_profile(args, card=True, template=arg.t)
            ) if not arg.v2 else asyncio.run(
                get_enka_profile2(args, huid=arg.hide_uid)
            )
            if error:
                return
            caption = f"{profile.player.name}'s profile"
            file_name = caption + ".png"
            path = "enka/" + file_name
            cprofile.card.save(path)
            event.reply_file(path, file_name, f"*{caption}*")
            return s_remove(path)
        if card:
            info = asyncio.run(get_gi_info(query=card))
            if not info:
                return event.reply(
                    f"*Character not found.*\nYou searched for {card}.\nNot what you searched for?\nTry again with double quotes"
                )
            char_id = info.get("id")
            result, error = asyncio.run(
                get_enka_card(
                    args, char_id, akasha=akasha, huid=arg.hide_uid, template=arg.t
                )
            ) if not arg.v2 else asyncio.run(
                get_enka_card2(
                    args, char_id, arg.hide_uid
                )
            )
            if error:
                return
            caption = f"{profile.player.name}'s current {info.get('name')} build"
            file_name = caption + ".png"
            path = "enka/" + file_name
            if not result.card:
                error = f"*{card} not found in showcase!*"
                return
            result.card[0].card.save(path)
            event.reply_file(path, file_name, f"*{caption}*")
            return s_remove(path)
        if cards:
            ids = str()
            errors = str()
            for name in cards.split(","):
                name = name.strip()
                info = asyncio.run(get_gi_info(query=name))
                if not info:
                    errors += f"{name}, "
                    continue
                char_id = info.get("id")
                ids += f"{char_id},"
            errors = errors.strip(", ")
            error_txt = f"*Character(s) not found.*\nYou searched for {errors}.\nNot what you searched for?\nTry again with double quotes"
            if not ids:
                return event.reply(error_txt)
            ids = ids.strip(",")
            result, error = asyncio.run(
                get_enka_card(
                    args, ids, akasha=akasha, huid=arg.hide_uid, template=arg.t
                )
            ) if not arg.v2 else asyncio.run(
                get_enka_card2(
                    args, ids, huid=arg.hide_uid
                )
            )
            if error:
                return

            if errors:
                event.reply(error_txt)
                time.sleep(1)
            return send_multi_cards(event, result, profile)
        if dump:
            result, error = asyncio.run(
                get_enka_card(
                    args, None, akasha=akasha, huid=arg.hide_uid, template=arg.t
                )
            ) if not arg.v2 else asyncio.run(
                get_enka_card2(
                    args, None, huid=arg.hide_uid
                )
            )
            if error:
                return
            return send_multi_cards(event, result, profile)
    except Exception:
        log(Exception)
    finally:
        if error:
            return event.reply(f"*Error:*\n{error}")


def send_multi_cards(event, results, profile):
    for card in results.card:
        print(card.name)
        caption = f"{profile.player.name}'s current {card.name} build"
        file_name = caption + ".png"
        path = "enka/" + file_name
        card.card.save(path)
        event.reply_file(path, file_name, f"*{caption}*")
        time.sleep(10)
        s_remove(path)


#def weapon_handler(event, args):
    