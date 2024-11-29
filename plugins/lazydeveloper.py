
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
import asyncio
# Initialize @LazyDeveloperr Instaloader 
from plugins.insta_lazydeveloper import download_from_lazy_instagram 
from plugins.tiktok_x_lazydeveloper import download_from_lazy_tiktok_and_x
from plugins.pintrest_lazydeveloepr import download_pintrest_vid
from plugins.youtube_downloader_lazydeveloper import youtube_and_other_download_lazy
from pyrogram import Client, filters
from pyrogram.types import Message
import re
from pyrogram import enums
from script import Script
import time
from collections import defaultdict
from lazydeveloper.database import db
from plugins.LazyDev_F_Sub import lazy_force_sub, is_subscribed

user_tasks = {}
# user_message_count = {}
user_message_count = defaultdict(list)


LAZY_REGEX = re.compile(
    pattern=r'(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))(.*)?')

@Client.on_message(filters.private & filters.text & ~filters.forwarded & ~filters.command(['start','users','broadcast']))
async def handle_incoming_message(client: Client, message: Message):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        user_id = message.from_user.id  # Get user ID dynamically
        # Extract the message text and user ID
            # if user_id not in ADMIN:
            #     await client.send_message(chat_id=message.chat.id, text=f"Sorry Sweetheart! cant talk to you \nTake permission from my Lover @LazyDeveloperr")
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id)

        if (FORCE_SUB_CHANNEL or FORCE_SUB_CHANNEL2 or FORCE_SUB_CHANNEL3) and not await is_subscribed(client, message):
            # User is not subscribed to any of the required channels, trigger force_sub logic
            return await lazy_force_sub(client, message) 
      
        # Message rate-limiting logic
        current_time = time.time()
        # Ensure the user has a list of message timestamps initialized
        if user_id not in user_message_count:
            user_message_count[user_id] = []

        # Filter out messages older than 1 second
        user_messages = user_message_count[user_id]
        user_message_count[user_id] = [timestamp for timestamp in user_messages if current_time - timestamp <= 5]  # Keep only messages within the last second
        message_count = len(user_message_count[user_id])  # Count messages sent in the last second
        
        # Check if the user exceeds the allowed maximum number of messages in 1 second
        if message_count >= MAXIMUM_TASK:
            await message.reply(Script.PLUS_SPAM_TEXT.format(MAXIMUM_TASK))
            return
        
        # Append the current message timestamp
        user_message_count[user_id].append(current_time)
        
        # assuming text sent by user @LazyDeveloperr
        match = LAZY_REGEX.search(message.text.strip())
        if not match:
            # No URL found in the message, ask the user to send a URL
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            ass = await message.reply(Script.WARNING_TEXT)
            await asyncio.sleep(6)
            await ass.delete()
            return
        # Initialize task list for the user if not already present
        if user_id not in user_tasks:
            user_tasks[user_id] = []

        # Check if the user already has 3 active tasks
        if len(user_tasks[user_id]) >= MAXIMUM_TASK:
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            sorry_lazy_sms = await message.reply(f"⏳ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ {MAXIMUM_TASK} ᴀᴄᴛɪᴠᴇ ᴅᴏᴡɴʟᴏᴀᴅs. ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ᴏɴᴇ ᴛᴏ ꜰɪɴɪsʜ ʙᴇғᴏʀᴇ ᴀddɪɴɢ ᴍᴏʀᴇ.")
            await asyncio.sleep(10)
            await sorry_lazy_sms.delete()
            return
        
        url = message.text.strip()
        asyncio.create_task(lazydeveloper_handle_url(client, message, url, user_id))
        return
    except Exception as lazyerror:
        print(f"error => {lazyerror}")

async def lazydeveloper_handle_url(client, message, url, user_id):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        ok = await message.reply("🔄 ᴅᴇᴛᴇᴄᴛɪɴɢ ᴜʀʟ ᴛʏᴘᴇ ᴀɴᴅ ᴘʀᴏᴄᴇssɪɴɢ ᴛʜᴇ ᴅᴏᴡɴʟᴏᴀᴅ...")

        # Check if the URL contains 'instagram.com'
        PLATFORM_HANDLERS = {
            "instagram.com": download_from_lazy_instagram,
            "tiktok.com": download_from_lazy_tiktok_and_x,
            "twitter.com": download_from_lazy_tiktok_and_x,
            "x.com": download_from_lazy_tiktok_and_x,
            "pin.it": download_pintrest_vid,
            "pinterest.com": download_from_lazy_tiktok_and_x,
            "facebook.com": download_from_lazy_tiktok_and_x,
            # "youtube.com": download_from_youtube,
            # "youtu.be": download_from_youtube
        }

        for platform, handler in PLATFORM_HANDLERS.items():
            if platform in url:
                await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
                lazydev = await ok.edit_text(f"Detected {platform} URL!")
                # Create a task for the handler function
                lazytask = asyncio.create_task(handler(client, message, url))
                user_tasks[user_id].append(lazytask)
                lazytask.add_done_callback(lambda t: asyncio.create_task(task_done_callback(client, message, user_id, t)))
                await lazydev.delete()
                return
            else:
                await ok.edit("😞 oᴏps! lᴏᴏks lɪᴋᴇ wᴇ'ʀᴇ nᴏᴛ frɪᴇnds wɪᴛʜ ᴛʜᴀᴛ lɪɴᴋ yᴇᴛ. 🌐💔 bᴜᴛ dᴏɴ'ᴛ wᴏʀʀʏ, wᴇ'ʀᴇ wᴏʀᴋɪɴɢ hᴀʀᴅ ᴛᴏ bʀɪɴɢ ɪᴛ ᴛᴏ ᴛʜᴇ pᴀʀᴛʏ! 🎉 sᴛᴀʏ ᴛᴜɴᴇᴅ! 👀")
                await client.send_message(LOG_CHANNEL, f"<b>🚨 ᴜɴᴋɴᴏᴡɴ ᴘʟᴀᴛꜰᴏʀᴍ ʟɪɴᴋ sᴇɴᴛ! 🧐</b>\n<b>ᴛʜᴇ ᴜsᴇʀ ᴇɴᴛᴇʀᴇᴅ ᴀ ʟɪɴᴋ ғʀᴏᴍ ᴀ ᴘʟᴀᴛꜰᴏʀᴍ ᴡᴇ ᴅᴏɴ'ᴛ ʀᴇᴄᴏɢɴɪᴢᴇ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ʟɪɴᴋ ᴏʀ ᴜᴘᴅᴀᴛᴇ ᴏᴜʀ ᴘʟᴀᴛꜰᴏʀᴍ ʜᴀɴᴅʟᴇʀ.</b>\n\n🔗hᴇʀᴇ ɪs ᴛʜᴇ ʟɪɴᴋ::\n{url}\nᴜsᴇʀ:{message.from_user.mention}")
    except Exception as e:
        # Handle any errors
        await ok.delete() if ok else None
        await lazydev.delete() if lazydev else None
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await client.send_message(message.chat.id, f"sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ.")
        print(f"❌ An error occurred: {e}")

async def task_done_callback(client, message, user_id, t):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        if user_id in user_tasks and t in user_tasks[user_id]:
            user_tasks[user_id].remove(t)

        # Notify the user
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        workdonemsg = await client.send_message(
            chat_id=message.chat.id,
            text="❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ..."
        )
        await asyncio.sleep(15)
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await workdonemsg.delete()
    except KeyError:
        print(f"Task or user ID not found during task cleanup: {t}")
    except Exception as e:
        print(f"Error in task_done_callback: {e}")

@Client.on_message(filters.private & filters.command(["spdl"]))
async def handle_seperate_download(client: Client, message: Message):
    # Extract the text after the command
    command_parts = message.text.split(maxsplit=1)  # Split the message into command and arguments
    if len(command_parts) < 2:
        await message.reply("⚠️ Please provide a valid URL after the command. Example: `/spdl <url>`")
        return
    
    url = command_parts[1].strip()  # Extract the URL part
    # Optional: Use regex to validate the URL format
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    if not url_pattern.match(url):
        await message.reply("⚠️ The provided text is not a valid URL. Please check and try again.")
        return

    # Inform the user about the process
    ok = await message.reply("🔄 Detecting URL type and processing the download...")
    
    # Call your download function
    await youtube_and_other_download_lazy(client, message, url)
    await ok.edit_text("Thank you for using me ❤")

@Client.on_message(filters.private & filters.forwarded)
async def handle_forwarded(client, message):
    try:
        user_id = message.from_user.id
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        ass = await message.reply(Script.NO_SPAM_TEXT)
        await asyncio.sleep(10)
        await ass.delete()
        return
    except Exception as lazyerror:
        print(f"Error occured : {lazyerror}")


# ============================================================================

# from pyrogram import Client, filters
# from pyrogram.types import Message
# from config import *
# from pyrogram.types import Message, InputMediaPhoto, InputMediaVideo
# import asyncio
# # Initialize @LazyDeveloperr Instaloader 
# from plugins.insta_lazydeveloper import download_from_lazy_instagram 
# from plugins.tiktok_x_lazydeveloper import download_from_lazy_tiktok_and_x
# from plugins.pintrest_lazydeveloepr import download_pintrest_vid
# from plugins.youtube_downloader_lazydeveloper import youtube_and_other_download_lazy
# from pyrogram import Client, filters
# from pyrogram.types import Message
# import re
# from pyrogram import enums

# @Client.on_message(filters.private & filters.command(["spdl"]))
# async def handle_seperate_download(client: Client, message: Message):
#     # Extract the text after the command
#     command_parts = message.text.split(maxsplit=1)  # Split the message into command and arguments
#     if len(command_parts) < 2:
#         await message.reply("⚠️ Please provide a valid URL after the command. Example: `/spdl <url>`")
#         return
    
#     url = command_parts[1].strip()  # Extract the URL part
#     # Optional: Use regex to validate the URL format
#     url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
#     if not url_pattern.match(url):
#         await message.reply("⚠️ The provided text is not a valid URL. Please check and try again.")
#         return

#     # Inform the user about the process
#     ok = await message.reply("🔄 Detecting URL type and processing the download...")
    
#     # Call your download function
#     await youtube_and_other_download_lazy(client, message, url, ok)
#     await ok.edit_text("Thank you for using me ❤")

# user_tasks = {}

# # async def handle_task_completion(user_id):
# #     """Wait for all active tasks to complete before allowing new ones."""
# #     if user_id in user_tasks:
# #         tasks = user_tasks[user_id]
# #         if tasks:
# #             await asyncio.gather(*tasks)  # Wait for all tasks to finish
# #             user_tasks[user_id] = []  # Clear tasks after completion

# # Your task completion callback function
# async def task_done_callback(client, message, user_id, t):
#     """
#     This function is called once the task is done to remove it from the user's task list
#     and send a completion message.
#     """
#     try:
#         # Remove the task from the user's task list
#         if t in user_tasks[user_id]:
#             user_tasks[user_id].remove(t)
        
#         # Send a message to inform the user that the task is completed
#         workdonemsg = await client.send_message(
#             chat_id=message.chat.id,
#             text="✅ Your task is completed. You can send a new URL now!"
#         )
        
#         # Optionally delete the completion message after some time
#         await asyncio.sleep(300)
#         await workdonemsg.delete()
    
#     except Exception as e:
#         print(f"Error in task_done_callback: {e}")


# @Client.on_message(filters.private & filters.text & ~filters.command(['start','users','broadcast','spdl']))
# async def handle_incoming_message(client: Client, message: Message):
#     try:
#         user_id = message.from_user.id  # Get user ID dynamically
#         # Extract the message text and user ID
#         if user_id not in ADMIN:
#             await client.send_message(chat_id=message.chat.id, text=f"Sorry Sweetheart! cant talk to you \nTake permission from my Lover @LazyDeveloperr")

#         # Check if the user already has 3 active tasks
#         if len(user_tasks[user_id]) >= 2:
#             await message.reply("⏳ You already have 2 active downloads. Please wait for one to finish before adding more.")
#             return

#         url = message.text.strip()

#         task = asyncio.create_task(lazydeveloper_handle_url(client, message, url, user_id))

#         # Initialize task list for the user if not already present
#         if user_id not in user_tasks:
#             user_tasks[user_id] = []

#         user_tasks[user_id].append(task)
#         # task.add_done_callback(lambda t: user_tasks[user_id].remove(t))

#         # Attach the done callback to remove the task and notify the user upon completion
#         task.add_done_callback(lambda t: asyncio.create_task(task_done_callback(client, message, user_id, t)))
#         # return

#         # while not task.done():
#         #     await asyncio.sleep(3)  # Sleep for 3 seconds before sending the next action
#         #     await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)  # Show the 'upload document' action
        
#         # async def task_done_callback(t):
#         #     user_tasks[user_id].remove(t)  # Remove the task from the user's task list
#         #     workdonemsg = asyncio.create_task(client.send_message(
#         #         chat_id=message.chat.id,
#         #         text="✅ Your task is completed. You can send a new URL now!"
#         #     ))
#         #     await asyncio.sleep(300)
#         #     await workdonemsg.delete()

#     except Exception as lazyerror:
#         print(lazyerror)


# async def lazydeveloper_handle_url(client, message, url, user_id):
#     try:
#         ok = await message.reply("🔄 ᴅᴇᴛᴇᴄᴛɪɴɢ ᴜʀʟ ᴛʏᴘᴇ ᴀɴᴅ ᴘʀᴏᴄᴇssɪɴɢ ᴛʜᴇ ᴅᴏᴡɴʟᴏᴀᴅ...")

#         # Check if the URL contains 'instagram.com'
#         PLATFORM_HANDLERS = {
#             "instagram.com": download_from_lazy_instagram,
#             "tiktok.com": download_from_lazy_tiktok_and_x,
#             "twitter.com": download_from_lazy_tiktok_and_x,
#             "x.com": download_from_lazy_tiktok_and_x,
#             "pin.it": download_pintrest_vid,
#             "pinterest.com": download_pintrest_vid,
#             "facebook.com": download_from_lazy_tiktok_and_x,
#             # "youtube.com": download_from_youtube,
#             # "youtu.be": download_from_youtube
#         }

#         for platform, handler in PLATFORM_HANDLERS.items():
#             if platform in url:
#                 lazydev = await ok.edit_text(f"Detected {platform} URL!")
#                 await lazydev.delete()
#                 # Create a task for the handler function
#                 task = asyncio.create_task(handler(client, message, url))
#                 # await handler(client, message, url)
#                 return
                
#                 # Create a task and add it to the user's task list
#                 # user_tasks[user_id].append(task)
                
#                 # while not task.done():
#                 #     await asyncio.sleep(3)  # Sleep for 3 seconds before sending the next action
#                 #     await message.reply_chat_action(enums.ChatAction.UPLOAD_DOCUMENT)  # Show the 'upload document' action

#                 # When the task finishes, remove it from the user's task list
#                 # task.add_done_callback(lambda t: user_tasks[user_id].remove(t))                
#                 # async def task_done_callback(t):
#                 #     user_tasks[user_id].remove(t)  # Remove the task from the user's task list
#                 #     workdonemsg = asyncio.create_task(client.send_message(
#                 #         chat_id=message.chat.id,
#                 #         text="✅ Your task is completed. You can send a new URL now!"
#                 #     ))
#                 #     await asyncio.sleep(300)
#                 #     await workdonemsg.delete()

#                 # task.add_done_callback(lambda t: user_tasks[user_id].remove(t))
                
#                 # return #await task  # Wait for the task to finish before proceeding

#         # for platform, handler in PLATFORM_HANDLERS.items():
#         #     if platform in url:
#         #         lazydev = await ok.edit_text(f"Detected {platform} ᴜʀʟ!")
#         #         await lazydev.delete()
#         #         await handler(client, message, url)
#         #         return

#     except Exception as e:
#         # Handle any errors
#         await message.reply(f"❌ An error occurred: {e}")

