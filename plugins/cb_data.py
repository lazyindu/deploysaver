
from plugins.dl_button import ddl_call_back
from plugins.button import youtube_dl_call_back

import asyncio

from youtube_dl import YoutubeDL
from pyrogram import enums
from pyrogram.types import Message
from pyrogram import Client, filters, enums

from config import *
from plugins.functions.help_ytdl import get_file_extension_from_url, get_resolution
YTDL_REGEX = r"^((?:https?:)?\/\/)"
from asyncio import sleep
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from script import Script

@Client.on_callback_query(filters.regex("^ytdl_audio$"))
async def callback_query_ytdl_audio(_, callback_query):
    try:
        url = callback_query.message.reply_to_message.text
        ydl_opts = {
            "cookies": "./cookies.txt",
            "format": "bestaudio",
            "outtmpl": "%(title)s - %(extractor)s-%(id)s.%(ext)s",
            "writethumbnail": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            message = callback_query.message
            await message.reply_chat_action(enums.ChatAction.TYPING)
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**Downloading audio...**")
            ydl.process_info(info_dict)
            # upload
            audio_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_audio(message, info_dict, audio_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            await message.reply_chat_action(enums.ChatAction.CANCEL)
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()


async def send_audio(message: Message, info_dict, audio_file):
    basename = audio_file.rsplit(".", 1)[-2]
    if info_dict["ext"] == "webm":
        audio_file_weba = f"{basename}.weba"
        os.rename(audio_file, audio_file_weba)
        audio_file = audio_file_weba
    thumbnail_url = info_dict["thumbnail"]
    thumbnail_file = f"{basename}.{get_file_extension_from_url(thumbnail_url)}"
    download_location = f"{DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"
    thumb = download_location if os.path.isfile(download_location) else None
    webpage_url = info_dict["webpage_url"]
    title = info_dict["title"] or ""
    caption = f'<b><a href="{webpage_url}">{title}</a></b>'
    duration = int(float(info_dict["duration"]))
    performer = info_dict["uploader"] or ""
    await message.reply_audio(
        audio_file,
        caption=caption,
        duration=duration,
        performer=performer,
        title=title,
        parse_mode=enums.ParseMode.HTML,
        thumb=thumb,
    )

    os.remove(audio_file)
    os.remove(thumbnail_file)


async def send_video(message: Message, info_dict, video_file):
    basename = video_file.rsplit(".", 1)[-2]
    thumbnail_url = info_dict["thumbnail"]
    thumbnail_file = f"{basename}.{get_file_extension_from_url(thumbnail_url)}"
    download_location = f"{DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"
    thumb = download_location if os.path.isfile(download_location) else None
    webpage_url = info_dict["webpage_url"]
    title = info_dict["title"] or ""
    caption = f'<b><a href="{webpage_url}">{title}</a></b>'
    duration = int(float(info_dict["duration"]))
    width, height = get_resolution(info_dict)
    await message.reply_video(
        video_file,
        caption=caption,
        duration=duration,
        width=width,
        height=height,
        parse_mode=enums.ParseMode.HTML,
        thumb=thumb,
    )

    os.remove(video_file)
    os.remove(thumbnail_file)


@Client.on_callback_query(filters.regex("^ytdl_video$"))
async def callback_query_ytdl_video(_, callback_query):
    try:
        # url = callback_query.message.text
        # url = callback_query.message.reply_to_message.text
        
        command_parts = message.text.split(maxsplit=1)  # Split the message into command and arguments
        if len(command_parts) < 2:
            await message.reply("⚠️ Please provide a valid URL after the command. Example: `/spdl <url>`")
            return
        
        url = command_parts[1].strip()
        ydl_opts = {
            "cookies": "./cookies.txt",
            "format": "best[ext=mp4]",
            "outtmpl": "%(title)s - %(extractor)s-%(id)s.%(ext)s",
            "writethumbnail": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            # message = callback_query.message
            await message.reply_chat_action(enums.ChatAction.TYPING)
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**Downloading video...**")
            ydl.process_info(info_dict)
            # upload
            video_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_video(message, info_dict, video_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)
            await message.reply_chat_action(enums.ChatAction.CANCEL)
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()


  
@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":

        await query.message.edit_text(
            text=Script.WELCOME_TEXT.format(query.from_user.mention),
            reply_markup=InlineKeyboardMarkup([
                [
                InlineKeyboardButton('• ᴜᴘᴅᴀᴛᴇꜱ •', url='https://t.me/lazydeveloper'),
                InlineKeyboardButton('• ꜱᴜᴘᴘᴏʀᴛ •', url='https://t.me/lazydeveloper')
                ],[
                InlineKeyboardButton("👑 • ᴏᴡɴᴇʀ • 💎", callback_data='own')
                ],[
                InlineKeyboardButton("❤ • ᴅᴇᴠ • 🍟", callback_data='dev')
                ],[
                InlineKeyboardButton('• ᴀʙᴏᴜᴛ •', callback_data='about'),
                InlineKeyboardButton('• ʜᴇʟᴘ •', callback_data='help')
                ]]),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
    elif data == "help":
        await query.message.edit_text(
            text=Script.HELP_TEXT.format(query.from_user.mention),
            reply_markup=InlineKeyboardMarkup([
                [
                InlineKeyboardButton("🔒 ᴄʟᴏꜱᴇ •", callback_data = "close"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ •", callback_data = "start")
               ]
               ]
            ),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif data == "about":
        await query.message.edit_text(
            text=Script.ABOUT_TXT.format(client.mention),
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup( [[
                InlineKeyboardButton("🔒 ᴄʟᴏꜱᴇ •", callback_data = "close"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ •", callback_data = "start")
               ]]
            ),
            parse_mode=enums.ParseMode.HTML
        )
    elif data == "dev":
        await query.message.edit_text(
            text=Script.DEVELOPER_TEXT.format(query.from_user.mention, client.mention, client.mention),
            reply_markup=InlineKeyboardMarkup( [[
                InlineKeyboardButton("🔒 ᴄʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data = "start")
               ]]
            ),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML 
        )
    elif data == "own":
        await query.message.edit_text(
            text=Script.OWNER_TEXT.format(TEL_USERNAME, TEL_NAME),
            reply_markup=InlineKeyboardMarkup( [[
                InlineKeyboardButton("🔒 ᴄʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("◀️ ʙᴀᴄᴋ", callback_data = "start")
               ]]
            ),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    elif "|" in data:
        await youtube_dl_call_back(client, query)
    elif "=" in data:
        await ddl_call_back(client, query)
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()

