from asyncio import sleep
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from lazydeveloper.database import db
from config import *
from plugins.LazyDev_F_Sub import lazy_force_sub, is_subscribed
from script import Script

@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id)

    if (FORCE_SUB_CHANNEL or FORCE_SUB_CHANNEL2 or FORCE_SUB_CHANNEL3) and not await is_subscribed(client, message):
        # User is not subscribed to any of the required channels, trigger force_sub logic
        return await lazy_force_sub(client, message) 
              
    button=InlineKeyboardMarkup([
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
        ]])
    if START_PIC:
        await message.reply_photo(START_PIC, caption=Script.WELCOME_TEXT.format(message.from_user.mention), reply_markup=button, parse_mode=enums.ParseMode.HTML)       
    else:
        await message.reply_text(text=Script.WELCOME_TEXT.format(message.from_user.mention), reply_markup=button, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
   


