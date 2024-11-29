from pyrogram import Client, filters, types
from pyrogram.types import Message
from io import BytesIO
import requests
import time
import os
import yt_dlp
import asyncio
import subprocess
from pyrogram import enums
from plugins.utitles import Mdata01
from config import TEL_USERNAME, TG_NORMAL_MAX_SIZE, LOG_CHANNEL

from lazydeveloper.lazyprogress import progress_for_pyrogram
from plugins.functions.help_ytdl import get_file_extension_from_url, get_resolution

import yt_dlp

def extract_caption_with_ytdlp(url):
    try:
        options = {
            'quiet': True,  # Suppress yt-dlp's output
            'skip_download': True,  # Don't download the video, only extract metadata
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)  # Extract metadata
            
            # Extract title and description
            title = info.get('title', 'No title available')
            description = info.get('description', '')
            video_id = info.get('id', None)
            # Extract the formats (audio or video)
            # formats = info.get('formats', [])
            # format_type = 'Unknown'
            # print(f"formats => {formats}")
            # print(f"video id => {video_id}")
            # # Check the formats and determine if it's audio or video
            # if formats:
            #     for fmt in formats:
            #         if fmt.get('vcodec') != 'none':  # Video format
            #             format_type = 'Video'
            #             break
            #         elif fmt.get('acodec') != 'none':  # Audio format
            #             format_type = 'Audio'
            #             break
            # print(f"Detected format => {format_type}")   
            return title, description, video_id

    except Exception as e:
        print(f"Error extracting caption with yt-dlp: {e}")
        return None, None, None

def reduce_quality_ffmpeg(video_path, output_path, target_size_mb=50):
    try:
        # Command to reduce video quality using ffmpeg
        command = [
            'ffmpeg', '-i', video_path,
            # Adjust the video bitrate (can be modified as needed)
            '-b:v', '500k',
            '-vf', 'scale=iw/2:ih/2',  # Reduce resolution by half
            '-c:a', 'aac',  # Encode audio with AAC
            '-b:a', '128k',  # Adjust the audio bitrate
            output_path
        ]

        # Execute the ffmpeg command
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error reducing video quality with ffmpeg: {e}")
        return False

async def download_video(url, destination_folder, message, format="video"):
    try:
        # Determine the format
        if format == "audio":
            format_type = 'bestaudio/best'
            ext = 'mp3'
        else:
            format_type = 'best'
            ext = 'mp4'

        # yt-dlp configuration with progress_hooks
        
        options = {
            # Use the video ID to avoid filename issues
            'outtmpl': f'{destination_folder}/%(id)s.%(ext)s',
            'format': format_type,  # Select the format based on user input
            'restrictfilenames': True,  # Limit special characters
            # 'writethumbnail': True,  #for thumbnails
            # Hook to show real-time progress
            # 'progress_hooks': [lambda d: asyncio.create_task(download_progress(d, message))],
        }

        # Download the video or audio
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error during download: {e}")
        return False

async def send_video(client, message: Message, info_dict, video_file, destination_folder, progress_message3, baseurl, platform):
    await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
    basename = video_file.rsplit(".", 1)[-2]
    thumbnail_url = info_dict["thumbnail"]
    video_id = info_dict.get('id', None)
    thumbnail_file = f"{basename}.{get_file_extension_from_url(thumbnail_url)}"
    download_location = f"{destination_folder}/{video_id}.jpg"
    thumb = download_location if os.path.isfile(download_location) else None
    webpage_url = info_dict["webpage_url"]
    title = info_dict["title"] or ""
    bot_username = client.username if client.username else TEL_USERNAME
    caption_lazy = f"ᴡɪᴛʜ ❤ @{bot_username}"
    caption = title if title else "===========🍟==========="
    while len(caption) + len(caption_lazy) > 1024:
        caption = caption[:-1]  # Trim caption if it's too long
    caption = f'<b><a href="{webpage_url}">{title}</a>\n\n<blockquote>{caption_lazy}</blockquote></b>'
    width, height, duration = await Mdata01(video_file)
    xlx = await progress_message3.edit_text("⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...")
    start_time = time.time()
    await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
    succ = await client.send_video(
        message.chat.id,
        video_file,
        caption=caption,
        duration=duration,
        width=width,
        height=height,
        parse_mode=enums.ParseMode.HTML,
        thumb=thumb,
        supports_streaming=True,
        progress=progress_for_pyrogram,
        progress_args=(
            f"<blockquote>🍟ᴜᴘʟᴏᴀᴅing ʏᴏᴜʀ ᴠɪᴅᴇᴏ... 📤</blockquote>============x============<blockquote><code>{caption}</code></blockquote>",
            xlx,
            start_time,
        )
    )
    await xlx.delete()
    if succ:
        # Send the video to the log channel with details
        org_cap = title[:97] + "..." if len(title) >= 100 else title

        caption = (
                f"<b>📂 ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜰᴏʀ ᴜsᴇʀ... ❤</b>"
                f"<blockquote><b>{org_cap}</b></blockquote>\n"
                f"<blockquote><b>🍿ᴘʟᴀᴛꜰᴏʀᴍ: {platform}</b></blockquote>\n"
                f"<blockquote>👤 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code></blockquote>\n"
                f"<blockquote>📩 <b>ɴᴀᴍᴇ:</b> {message.from_user.mention}</blockquote>\n"
                f"<blockquote>🔗 <b>ᴜʀʟ:</b> {baseurl}</blockquote>"
            )
        await client.copy_message(
                    chat_id=LOG_CHANNEL,
                    from_chat_id=message.chat.id,
                    message_id=succ.id,
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML
                )

    if os.path.exists(video_file):
        os.remove(video_file)
    if os.path.exists(thumbnail_file):
        os.remove(thumbnail_file)


async def download_from_lazy_tiktok_and_x(client, message, url, platform):
    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        progress_message2 = await message.reply("<i>⚙ ᴘʀᴇᴘᴀʀɪɴɢ\nᴀɴᴀʟʏsɪɴɢ yᴏᴜʀ ᴜʀʟ...</i>")
        TEMP_DOWNLOAD_FOLDER = f"./downloads/{message.from_user.id}/{time.time()}"
        if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
            os.makedirs(TEMP_DOWNLOAD_FOLDER)
        # Using the temporary download folder
        destination_folder = TEMP_DOWNLOAD_FOLDER
        baseurl = url
        # try:
        ydl_opts = {
        "format": "best[ext=mp4]",
        'outtmpl': f'{destination_folder}/%(id)s.%(ext)s',
        "writethumbnail": True,
        'socket_timeout': 60,  # Increase the timeout to 60 seconds
        # 'http_chunk_size': 10485760,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            await progress_message2.edit("<i>⚙ fᴇᴛᴄʜɪɴɢ ʀᴇQᴜɪʀᴇᴅ dᴇᴛᴀɪʟs fʀᴏᴍ yᴏᴜʀ lɪɴᴋ...</i>")
            info_dict = ydl.extract_info(url, download=False)
            ydl.process_info(info_dict)
            # upload
            video_file = ydl.prepare_filename(info_dict)
            try:
                # print(f"processing vide0 send => {video_file}")
                await send_video(client, message, info_dict, video_file, destination_folder, progress_message2, baseurl, platform)
            except Exception as lazy:
                print(f"Error in task => {lazy}")
    except Exception as e:
        await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)
        await client.send_message(message.chat.id, f"sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ.")
        print(f"❌ An unexpected error occurred: {e}")
        await progress_message2.delete()

        
        
        
        
        
        
# =========================================metod-2-slow-method================================        
        
        
        # await asyncio.sleep(1)
        
        # await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

        # try:
        #     title, description, video_id = extract_caption_with_ytdlp(url)
        #     print(f"Title => : {title}")
        # except Exception as LazyDeveloper:
        #     print(LazyDeveloper)
        #     pass


        # new_caption = title if title else " "
        # while len(new_caption) + len(caption_lazy) > 1024:
        #     new_caption = new_caption[:-1]  # Trim caption if it's too long
        # new_caption = new_caption + caption_lazy  # Add bot username at the end
        # Initialize media list
    
        # format = "video"
        # TEMP_DOWNLOAD_FOLDER = f"./downloads/{message.from_user.id}/{time.time()}"
        # if not os.path.exists(TEMP_DOWNLOAD_FOLDER):
        #     os.makedirs(TEMP_DOWNLOAD_FOLDER)
        # # Using the temporary download folder
        # destination_folder = TEMP_DOWNLOAD_FOLDER  
        # print(f"destination_folder => {destination_folder}")
        # Start the do  wnload and update the same message
        # success_download = asyncio.create_task(download_video(url, destination_folder, progress_message2, format))
        # print(f"Download success")

        # thumb_location = f"{destination_folder}/{video_id}.jpg"
        # thumb = thumb_location if os.path.isfile(thumb_location) else None
        # print(f"Thumb location => {thumb_location}")
        
        # if not success_download:
        #     await progress_message2.edit_text('Error during the video download. Please try again later.')
        #     return

        # Get the name of the downloaded file
        # video_filename = max([os.path.join(destination_folder, f) for f in os.listdir(
        #     destination_folder)], key=os.path.getctime)
        # print(f"video filename:{video_filename}")

        # Check the file size
        # file_size_mb = os.path.getsize(video_filename) / (1024 * 1024)
        # if file_size_mb > TG_NORMAL_MAX_SIZE:
        #     lzz = await message.reply_text(f'The file is too large ({file_size_mb:.2f} MB). '
        #                             f'Reducing the quality to meet the  limit...')

        #     # Attempt to reduce the quality using ffmpeg
        #     output_filename = os.path.join(
        #         destination_folder, 'compressed_' + os.path.basename(video_filename))
        #     success_reduce = reduce_quality_ffmpeg(
        #         video_filename, output_filename, TG_NORMAL_MAX_SIZE)

        #     if not success_reduce:
        #         await lzz.edit_text('Error reducing the video quality. Please try again later.')
        #         return
        #     await lzz.delete()


        #     # Switch to the compressed file for sending
        #     video_filename = output_filename

        # Send the video/audio file to the user
        # progress_message3 = await progress_message2.edit_text("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>")
        # await asyncio.sleep(1)
        

        # try:
        #     # await upload_processor(client, message, url, video_filename)
            # width, height, duration = await Mdata01(video_filename)
       
            # await client.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_VIDEO)
        #     # print("Download complete. Sending now...")

        #     # print(f"w->{width}--h->{height}--d->{duration}")
        #     start_time = time.time()
        #     await client.send_video(
        #             chat_id=message.chat.id,
        #             video=open(video_filename, 'rb'),
        #             caption=new_caption,
        #             duration=duration,
        #             width=width,
        #             height=height,
        #             # thumb=thumb,
        #             supports_streaming=True,
        #             parse_mode=enums.ParseMode.HTML,
        #             progress=progress_for_pyrogram,
        #             progress_args=(
        #                 f"<blockquote>🍟ᴜᴘʟᴏᴀᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ... 📤</blockquote>============x============<blockquote>{new_caption}</blockquote>",
        #                 progress_message3,
        #                 start_time,
        #             ))
    
    # ----------------------------method 3-----------------
    #     try:
    #         ydl_opts = {
    #         "cookies": "./cookies.txt",
    #         "format": "best[ext=mp4]",
    #         'outtmpl': f'{destination_folder}/%(id)s.%(ext)s',
    #         "writethumbnail": True,
    #         'socket_timeout': 60,  # Increase the timeout to 60 seconds
    #         'http_chunk_size': 10485760,
    #         }
    #         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #             progress_message3 = await progress_message2.edit_text("<i>⚡ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ...</i>")
    #             info_dict = ydl.extract_info(url, download=False)
    #             ydl.process_info(info_dict)
    #             # upload
    #             video_file = ydl.prepare_filename(info_dict)
    #             print(f"video_file=> {video_file}")
    #             try:
    #                 await send_video(message, info_dict, video_file, destination_folder, progress_message3)
    #             except Exception as lazy:
    #                 print(f"Error in task => {lazy}")
                
    #     except Exception as e:
    #         await client.send_message(message.chat.id, f'sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ.')
    #         print(f"Error sending the file: {e}")
    #     finally:
    #         lazydeveloper = await client.send_message(chat_id=message.chat.id, text=f"❤ ꜰᴇᴇʟ ꜰʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜰʀɪᴇɴᴅ ᴄɪʀᴄʟᴇ...")
    #         await asyncio.sleep(100)
    #         await lazydeveloper.delete()
    # except Exception as e:
    #     await client.send_message(message.chat.id, f"sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ...\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ.")
    #     print(f"❌ An unexpected error occurred: {e}")
