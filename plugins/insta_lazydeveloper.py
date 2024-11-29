import instaloader
import re
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
insta = instaloader.Instaloader()
from pyrogram import enums
from instaloader.exceptions import (
    ConnectionException,
    PrivateProfileNotFollowedException,
    LoginRequiredException,
    BadResponseException,
    TooManyRequestsException,
)
from plugins.tiktok_x_lazydeveloper import download_from_lazy_tiktok_and_x

async def initiliselazyinsta(Lazy, post_shortcode):
    post = instaloader.Post.from_shortcode(Lazy.context, post_shortcode)
    return post

async def download_from_lazy_instagram(client, message, url):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    progress_message2 = await message.reply("<i>⚙ fᴇᴛᴄʜɪɴɢ ʀᴇQᴜɪʀᴇᴅ dᴇᴛᴀɪʟs fʀᴏᴍ yᴏᴜʀ lɪɴᴋ...</i>")
    try:
        # Extract shortcode from Instagram URL (assuming this is a function you implemented)
        
        post_shortcode = get_post_or_reel_shortcode_from_link(url)
        
        if not post_shortcode:
            print(f"log:\n\nuser: {message.chat.id}\n\nerror in getting post_shortcode")
            await progress_message2.edit("❌ Invalid Instagram link provided.")
            return  # Post shortcode not found, stop processing
        
        await asyncio.sleep(1)
        
        # Get an instance of Instaloader 
        L = get_ready_to_work_insta_instance()        
        lazytask = asyncio.create_task(initiliselazyinsta(L, post_shortcode))
        post = await lazytask
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        # Caption handling (ensure the caption does not exceed Telegram's limit)
        bot_username = client.username if client.username else TEL_USERNAME
        caption_trail = "\n\n" + f"<blockquote>ᴡɪᴛʜ ❤ @{bot_username}</blockquote>"

        try:
            new_caption = post.caption if post.caption else "==========🍟=========="
        except Exception as lazyerror:
            print(f"Caption not loaded : {lazyerror}")
            pass
        while len(new_caption) + len(caption_trail) > 1024:
            new_caption = new_caption[:-1]  # Trim caption if it's too long
        new_caption = new_caption + caption_trail  # Add bot username at the end
        # Initialize media list
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await progress_message2.edit("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>")
        # await asyncio.sleep(1)
        
        media_list = []
        # Handle sidecars (multiple media in a post)
        if post.mediacount > 1:
            sidecars = post.get_sidecar_nodes()
            for s in sidecars:
                if s.is_video:
                    url = s.video_url
                    media = InputMediaVideo(url)
                    if not media_list:  # Add caption to the first media
                        media = InputMediaVideo(url, caption=new_caption)
                else:
                    url = s.display_url
                    media = InputMediaPhoto(url)
                    if not media_list:  # Add caption to the first media
                        media = InputMediaPhoto(url, caption=new_caption)
                media_list.append(media)

            # Send media group
            await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_DOCUMENT)
            lazymedia = await client.send_media_group(message.chat.id, media_list, parse_mode=enums.ParseMode.HTML)

        else:
            # Single media handling
            if post.is_video:
                await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
                lazymedia = await client.send_video(message.chat.id, post.video_url, caption=new_caption, parse_mode=enums.ParseMode.HTML)
            else:
                await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
                lazymedia = await client.send_photo(message.chat.id, post.url, caption=new_caption, parse_mode=enums.ParseMode.HTML)
        
        await progress_message2.delete()
        if lazymedia:
        # Send the video to the log channel with details
            org_cap = new_caption[:97] + "..." if len(new_caption) >= 100 else new_caption

            caption = (
                    f"<b>📂ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜰᴏʀ ᴜsᴇʀ... ❤</b>"
                    f"<blockquote><b>{org_cap}</b></blockquote>\n"
                    f"<blockquote>👤 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code></blockquote>\n"
                    f"<blockquote>📩 <b>ɴᴀᴍᴇ:</b> {message.from_user.mention}</blockquote>\n"
                    f"<blockquote>🔗 <b>ᴜʀʟ:</b> {url}</blockquote>"
                )
            await client.copy_message(
                        chat_id=LOG_CHANNEL,
                        from_chat_id=message.chat.id,
                        message_id=lazymedia.id,
                        caption=caption,
                        parse_mode=enums.ParseMode.HTML
                    )

    except ConnectionException:
        await progress_message2.edit("🚨 Connection error. Please try again later.")
    except PrivateProfileNotFollowedException:
        await progress_message2.edit("🔒 Cannot access this profile. It's private, and i don't follow it. Please send me public urls")
    except LoginRequiredException:
        await progress_message2.edit("🔑 This operation requires login. Please send me public urls")
    except BadResponseException:
        respond = await progress_message2.edit("⚠️ Instagram returned an unexpected response. Please try again.")
        await client.send_chat_action(message.chat.id, enums.ChatAction.Typing)
        lazydeveloperr = await client.send_message(message.chat.id, f"Changing algorithm...")
        await asyncio.sleep(1)
        await lazydeveloperr.edit(f"Trying with advance method...")
        try:
            lazybhaiya = asyncio.create_task(download_from_lazy_tiktok_and_x(client, message, url))
            print(f"method changed for user {message.from_user.id} => url = {url}")
            await lazybhaiya
            await respond.delete()
            return 
        except Exception as lazyerror:
            print(lazyerror)
    except TooManyRequestsException:
        await progress_message2.edit("⏳ Too many requests! Instagram is rate-limiting you. Please wait and try again.")
    except Exception as lze:
        await progress_message2.edit(f"😕 An unexpected error occurred, Please try again later.")
        print(f"😕 An unexpected error occurred : {lze}")
        await progress_message2.delete()

# regex
insta_post_or_reel_reg = r'(?:https?://www\.)?instagram\.com\S*?/(p|reel)/([a-zA-Z0-9_-]{11})/?'

def get_post_or_reel_shortcode_from_link(link):
    match = re.search(insta_post_or_reel_reg, link)
    if match:
        return match.group(2)
    else:
        return False

def get_ready_to_work_insta_instance():
    L = instaloader.Instaloader()
    return L
