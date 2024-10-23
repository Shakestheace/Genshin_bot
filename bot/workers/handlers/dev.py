import io
import sys
import traceback

from bot import log_file_name
from bot.utils.bot_utils import split_text
from bot.utils.msg_utils import get_args, user_is_owner
from bot.utils.os_utils import read_n_to_last_line


def eval_handler(event, cmd):
    """
    Evaluate and execute code within bot.
    Global namespace has been cleaned so you'll need to manually import modules

    USAGE:
    Command requires code to execute as arguments.
    For example /eval print("Hello World!")
    Kindly refrain from adding whitelines and newlines between command and argument.
    """
    if not user_is_owner(event.user.id):
        return
    # msg = await event.reply("Processing ...")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    if len(evaluation) > 4000:
        final_output = "EVAL: {} \n\n OUTPUT: \n{} \n".format(cmd, evaluation)
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            event.reply_file(
                out_file,
                out_file.name,
                caption=cmd,
            )
    else:
        final_output = "*Python3:*\n```{}```\n\n*Output:*\n```{}```\n".format(
            cmd, evaluation
        )
        event.reply(final_output)


def aexec(code, event):
    exec(f"def __aexec(event): " + "".join(f"\n {l}" for l in code.split("\n")))
    return locals()["__aexec"](event)


def getlogs(event, args):
    """
    Upload bots logs in txt format.
    Or as a message if '-t' *Number is used

    *Number is the line number to begin from in log file except '0'
    """
    user = event.user.id
    if not user_is_owner(user):
        return
    if not args:
        return event.reply(file=log_file_name, file_name=log_file_name)
    arg = get_args("-t", to_parse=args)
    if arg.t and arg.t.isdigit() and (ind := int(arg.t)):
        msg = str()
        for i in reversed(range(1, ind)):
            msg += read_n_to_last_line(log_file_name, i)
            msg += "\n"
        msg = "Nothing Here.\nTry with a higher number" if not msg else msg
        pre_event = event
        for smsg in split_text(msg):
            smsg = f"```\n{smsg}\n```"
            pre_event = pre_event(smsg, quote=True)
            time.sleep(5)
    else:
        return getlogs(event, None)
