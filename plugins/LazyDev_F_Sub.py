from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from random import choice

from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client,  __version__, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired,UserNotParticipant
from config import *
logger = logging.getLogger(__name__)


async def is_subscribed(bot, query):
    required_channels = [FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3]
    for channels in required_channels:
        try:
            user = await bot.get_chat_member(channels, query.from_user.id)
        except UserNotParticipant:
            pass
        except Exception as e:
            logger.exception(e)
        else:
            if user.status != enums.ChatMemberStatus.BANNED:
                return True
    return False

async def lazy_force_sub(client: Client, message: Message):
    try:
        invite_link = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL), creates_join_request=True)
        invite_link2 = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL2), creates_join_request=True)
        invite_link3 = await client.create_chat_invite_link(int(FORCE_SUB_CHANNEL3), creates_join_request=True)
    except ChatAdminRequired:
        logger.error("Hey Sona, Ek dfa check kr lo ki auth Channel mei Add hu ya nhi...!")
        return
    buttons = [
        
            [InlineKeyboardButton(text="📌ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ1", url=invite_link.invite_link)],
            [InlineKeyboardButton(text="📌ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ2", url=invite_link2.invite_link)],
            [InlineKeyboardButton(text="📌ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ3", url=invite_link3.invite_link)],
        
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='↺ʀᴇʟᴏᴀᴅ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass
    # setting up multiple message for force sub msg LazyDeveloperr
    lazydeveloperquotes = [
    "<blockquote>🌟{} \n <b>ɢʀᴇᴀᴛ ᴛʜɪɴɢs ɴᴇᴠᴇʀ ᴄᴀᴍᴇ ꜰʀᴏᴍ ᴄᴏᴍꜰᴏʀᴛ ᴢᴏɴᴇs.</b>\n sᴛᴇᴘ ɪɴ ᴀɴᴅ ᴊᴏɪɴ ᴜs ꜰᴏʀ ᴇxᴄɪᴛɪɴɢ ᴜᴘᴅᴀᴛᴇs!</blockquote>",
    "<blockquote>🚀{} \n <b>sᴛᴀʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ, sᴛᴀʏ ɪɴsᴘɪʀᴇᴅ.</b>\n ʜɪᴛ ᴛʜᴇ ᴊᴏɪɴ bᴜᴛᴛᴏɴ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍᴏʀᴇ!</blockquote>",
    "<blockquote>✨{} \n <b>ᴅʀᴇᴀᴍ bɪɢ, ᴀᴄᴛ bɪɢɢᴇʀ.</b>\n sᴛᴀʏ wɪᴛʜ ᴜs ꜰᴏʀ ᴀᴍᴀᴢɪɴɢ ᴄᴏɴᴛᴇɴᴛ!</blockquote>",
    "<blockquote>💡{} \n <b>ᴋɴᴏᴡʟᴇᴅɢᴇ ɪs ᴘᴏᴡᴇʀ.</b>\n jᴏɪɴ ᴜs nᴏᴡ ᴀɴᴅ nᴇᴠᴇʀ mɪss ᴀɴ ᴜᴘᴅᴀᴛᴇ!</blockquote>",
    "<blockquote>🔥{} \n <b>ʏᴏᴜʀ jᴏᴜʀɴᴇʏ ᴛᴏ ɢʀᴇᴀᴛɴᴇss ʙɪɢɪɴs ʜᴇʀᴇ.</b> ᴛᴀᴘ ᴛʜᴇ bᴜᴛᴛᴏɴ ᴛᴏ jᴏɪɴ nᴏᴡ!</blockquote>",
    "<blockquote>🎉{} \n <b>ʙᴇ ᴘᴀʀᴛ ᴏꜰ sᴏᴍᴇᴛʜɪɴɢ ᴀᴍᴀᴢɪɴɢ.</b>\n jᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴛʜᴇ ᴍᴀɢɪᴄ!</blockquote>",
    "<blockquote>📚{} \n <b>sᴛᴀʏ ɪɴғᴏʀᴍᴇᴅ, sᴛᴀʏ ᴀʜᴇᴀᴅ.</b>\n jᴏɪɴ nᴏᴡ ꜰᴏʀ ᴛʜᴇ ʟᴀᴛᴇsᴛ ᴜᴘᴅᴀᴛᴇs!</blockquote>",
    "<blockquote>💪{} \n <b>ᴛᴏɢᴇᴛʜᴇʀ, wᴇ ɢʀᴏᴡ sᴛʀᴏɴɢᴇʀ.</b>\n ᴅᴏɴ'ᴛ mɪss ᴏᴜᴛ—jᴏɪɴ ᴜs ᴛᴏᴅᴀʏ!</blockquote>",
    "<blockquote>🌈{} \n <b>ᴜɴʟᴏᴄᴋ ᴀ ᴡᴏʀʟᴅ ᴏғ ᴘᴏssɪʙɪʟɪᴛɪᴇs.</b>\n ᴛᴀᴘ bᴇʟᴏᴡ ᴛᴏ sᴛᴀʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ!</blockquote>",
    "<blockquote>🌟{} \n <b>ʏᴏᴜʀ sᴜᴘᴘᴏʀᴛ ꜰᴜᴇʟs ᴏᴜʀ jᴏᴜʀɴᴇʏ.</b>\n jᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ bᴇ ᴘᴀʀᴛ ᴏꜰ ᴛʜᴇ ꜰᴀᴍɪʟʏ!</blockquote>"
]

    # Randomly select a quote
    text = choice(lazydeveloperquotes)

    await message.reply(
        text=text.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.HTML

    )
