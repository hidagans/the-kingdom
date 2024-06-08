import os
import platform
import random
import subprocess
import sys
import traceback
from asyncio import sleep
from io import StringIO
from subprocess import PIPE, Popen, TimeoutExpired
from sys import version as pyver
from time import perf_counter

import psutil
from aiofiles import open as aopen
from aiofiles.os import remove as aremove
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import FloodWait
from pytgcalls.__version__ import __version__ as pytgver

from kingdom import bot
from kingdom.database import *
from kingdom.core import KING, FILTERS


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "\n c = kingdom = client"
        + "\n m = message"
        + "\n r = message.reply_to_message"
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)



@KING.CMD("update", FILTERS.OWNER)
async def update(_, message):
    try:
        out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
        if "Already up to date." in str(out):
            return await message.reply_text("Bot Updated ✅")
        await message.reply_text(f"{out}")
    except Exception as e:
        return await message.reply_text(str(e))
    await message.reply_text("<b>Updated with default branch, restarting now.</b>")
    os.system(f"kill -9 {os.getpid()} && bash start")


@KING.CMD("restart", FILTERS.OWNER)
async def restart(_, message):
      try:
          await message.reply("Bot restarted ✅")
          os.system(f"kill -9 {os.getpid()} && bash start")
      except Exception as e:
          await message.reply(e)


@KING.CMD("eval", FILTERS.OWNER)
async def evaluate(client, message):
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except:
        return await message.reply("乁⁠(⁠ ⁠•⁠_⁠•⁠ ⁠)⁠ㄏ")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
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
    final_output = f"<b>Output</b>:\n    <code>{evaluation.strip()}</code>"
    if len(final_output) > 4096:
        filename = "output.txt"
        async with aopen(filename, "w+", encoding="utf8") as out_file:
            await out_file.write(str(final_output))
        await message.reply_document(
            document=filename,
            caption=cmd,
            disable_notification=True,
            quote=True,
        )
        await aremove(filename)
    else:
        await message.reply(final_output)


@KING.CMD("br|broadcast", FILTERS.OWNER)
async def bruser_message(client, message):
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("text or reply to message")
        query = message.text.split(None, 1)[1]
    susr = 0
    served_users = []
    susers = await get_served_users()
    for user in susers:
        served_users.append(int(user["user_id"]))
    for i in served_users:
        try:
            m = (
                await bot.forward_messages(i, y, x)
                if message.reply_to_message
                else await bot.send_message(i, text=query)
            )
            susr += 1
        except FloodWait as e:
            flood_time = int(e.x)
            if flood_time > 200:
                continue
            await sleep(flood_time)
        except Exception:
            pass
    try:
        await message.reply_text("Broadcast Success to {} user".format(susr))
    except:
        pass


@KING.CMD("shell|sh", FILTERS.OWNER)
async def example_edit(client, message):
    if not message.reply_to_message and len(message.command) == 1:
        return await message.reply("Specify the command in message text or in reply")
    cmd_text = (
        message.text.split(maxsplit=1)[1]
        if message.reply_to_message is None
        else message.reply_to_message.text
    )
    cmd_obj = Popen(cmd_text, shell=True, stdout=PIPE, stderr=PIPE, text=True)

    anu = await message.reply("Running...")
    text = f"$ <code>{cmd_text}</code>\n\n"
    try:
        start_time = perf_counter()
        stdout, stderr = cmd_obj.communicate(timeout=60)
    except TimeoutExpired:
        text += "<b>Timeout expired (60 seconds)</b>"
    else:
        stop_time = perf_counter()
        if stdout:
            stdout_output = f"{stdout}"
            text += "<b>Output:</b>\n" f"<code>{stdout}</code>\n"
        else:
            stdout_output = ""

        if stderr:
            stderr_output = f"{stderr}"
            text += "<b>Error:</b>\n" f"<code>{stderr}</code>\n"
        else:
            stderr_output = ""

        time = round(stop_time - start_time, 3) * 1000
        text += (
            f"<b>Completed in {time} miliseconds with code {cmd_obj.returncode}</b> "
        )

    try:
        await anu.edit(text)
    except:
        output = f"{stdout_output}\n\n{stderr_output}"
        command = f"{cmd_text}"

        await anu.edit("Result too much, send with document...")

        i = random.randint(1, 9999)
        async with aopen(f"result{i}.txt", "w") as file:
            await file.write(f"{output}")

        try:
            await message.reply_document(
                message.chat.id,
                f"temp/result{i}.txt",
                caption=f"<code>{command}</code>",
            )
            await anu.delete()
        except:
            await message.reply_document(f"result{i}.txt", caption="Result")
            await anu.edit(f"<code>{command}</code>")
        await aremove(f"result{i}.txt")
    cmd_obj.kill()


@KING.CMD("stats", FILTERS.OWNER)
async def bruser_stats(client, message):
    stats = len(await get_served_users())
    await message.reply(f"Stats user: {stats}")


@KING.CMD("sistem", FILTERS.OWNER)
async def sistem_stats(client, message):
    sc = platform.system()
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}MHz"
    except:
        cpu_freq = "Unable to Fetch"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    total = str(total)
    used = hdd.used / (1024.0**3)
    used = str(used)
    free = hdd.free / (1024.0**3)
    free = str(free)

    text = f""" **⚙️ Kingdom Bot Sistem...**

**Platform:** {sc}
**Ram:** 64
**Physical Cores:** 32
**Total Cores:** 32
**Cpu Frequency:** {cpu_freq}

**Python Version :** {pyver.split()[0]}
**Pyrogram Version :** {pyrover}
**Py-TgCalls Version :** {pytgver}

**Storage Avail:** {total[:4]} GiB
**Storage Used:** {used[:4]} GiB
**Storage Left:** {free[:4]} GiB
    """

    await message.reply(text)
