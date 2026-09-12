import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import Config
from database import db

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Temporary state tracker for setting custom values
USER_STATES = {}

def to_smallcaps(text: str) -> str:
    """Converts standard lowercase/uppercase English alphabets into aesthetic Smallcaps unicode."""
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    
    small_upper = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋ𝚕ᴍɴᴏᴩqʀꜱᴛᴜᴠᴡxyᴢ"
    small_lower = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋ𝚕ᴍɴᴏᴩqʀꜱᴛᴜᴠᴡxyᴢ"
    
    trans_table = str.maketrans(uppercase + lowercase, small_upper + small_lower)
    return text.translate(trans_table)

async def is_user_subscribed(bot, user_id: int) -> bool:
    """Checks if the user is a member of both mandatory F-Sub channels."""
    if not Config.CHANNEL_1_ID or not Config.CHANNEL_2_ID:
        return True  
        
    for channel_id in [Config.CHANNEL_1_ID, Config.CHANNEL_2_ID]:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in ["creator", "administrator", "member"]:
                return False
        except Exception as e:
            logger.error(f"F-Sub check error for channel {channel_id}: {e}")
            return False
    return True

async def send_fsub_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the locked F-Sub requirement message."""
    keyboard = [
        [
            InlineKeyboardButton("📢 Channel 1", url=Config.CHANNEL_1_LINK),
            InlineKeyboardButton("📢 Channel 2", url=Config.CHANNEL_2_LINK),
        ],
        [InlineKeyboardButton("🔄 Try Again", callback_data="check_fsub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"⚠️ **{to_smallcaps('Access Restricted')}**\n\n"
        f"{to_smallcaps('To use this bot, you must join both of our official channels. ')}"
        f"{to_smallcaps('Please join using the buttons below and click')} **{to_smallcaps('Try Again')}**."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and F-Sub verification."""
    user = update.effective_user
    await db.add_user(user.id)

    if not await is_user_subscribed(context.bot, user.id):
        await send_fsub_message(update, context)
        return

    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main bot welcome interface."""
    keyboard = [
        [InlineKeyboardButton(f"⚙️ {to_smallcaps('Settings Hub')}", callback_data="open_settings")],
        [
            InlineKeyboardButton(f"ℹ️ {to_smallcaps('About')}", callback_data="about_menu"),
            InlineKeyboardButton(f"📢 {to_smallcaps('Updates')}", url=Config.UPDATE_CHANNEL)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"🔥 **{to_smallcaps('Welcome to Deadpool Audio Renamer!')}**\n\n"
        f"{to_smallcaps('I can help you rename audio tracks, inject metadata, customize thumbnails, ')}"
        f"{to_smallcaps('and apply personal captions automatically.')}\n\n"
        f"{to_smallcaps('Choose an option below to manage your preferences:')}"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def settings_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the user settings status card and configuration options."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    settings = await db.get_user_settings(user_id) or {}
    
    thumb_status = f"✅ {to_smallcaps('Set')}" if settings.get("thumbnail") else f"❌ {to_smallcaps('Not Set')}"
    caption_status = f"`{settings.get('caption')}`" if settings.get("caption") else f"❌ {to_smallcaps('Not Set')}"
    title_status = f"`{settings.get('audio_title')}`" if settings.get("audio_title") else f"❌ {to_smallcaps('Not Set')}"
    artist_status = f"`{settings.get('artist_name')}`" if settings.get("artist_name") else f"❌ {to_smallcaps('Not Set')}"

    text = (
        f"⚙️ **{to_smallcaps('User Settings Dashboard')}**\n\n"
        f"👤 **{to_smallcaps('User ID')}:** `{user_id}`\n"
        f"🖼️ **{to_smallcaps('Permanent Thumbnail')}:** {thumb_status}\n"
        f"📝 **{to_smallcaps('Custom Caption')}:** {caption_status}\n"
        f"🎵 **{to_smallcaps('Audio Title/Header')}:** {title_status}\n"
        f"🎙️ **{to_smallcaps('Artist Name')}:** {artist_status}\n\n"
        f"{to_smallcaps('Select a category below to configure:')}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"🖼️ {to_smallcaps('Thumbnail')}", callback_data="menu_thumb"),
            InlineKeyboardButton(f"📝 {to_smallcaps('Caption')}", callback_data="menu_caption")
        ],
        [
            InlineKeyboardButton(f"🎵 {to_smallcaps('Audio Title')}", callback_data="menu_title"),
            InlineKeyboardButton(f"🎙️ {to_smallcaps('Artist')}", callback_data="menu_artist")
        ],
        [InlineKeyboardButton(f"🔙 {to_smallcaps('Main Menu')}", callback_data="main_menu")]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def sub_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles sub-menus for specific setting categories."""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    category_map = {
        "menu_thumb": ("Thumbnail", "thumbnail"),
        "menu_caption": ("Custom Caption", "caption"),
        "menu_title": ("Audio Title", "audio_title"),
        "menu_artist": ("Artist Name", "artist_name")
    }
    
    for prefix, (name, key) in category_map.items():
        if data == prefix:
            USER_STATES.pop(query.from_user.id, None)
            keyboard = [
                [
                    InlineKeyboardButton(f"📤 {to_smallcaps('Set')}", callback_data=f"set_{key}"),
                    InlineKeyboardButton(f"👁️ {to_smallcaps('View')}", callback_data=f"view_{key}")
                ],
                [
                    InlineKeyboardButton(f"🗑️ {to_smallcaps('Delete')}", callback_data=f"del_{key}"),
                    InlineKeyboardButton(f"🔙 {to_smallcaps('Settings')}", callback_data="open_settings")
                ]
            ]
            if key == "caption":
                keyboard.insert(1, [InlineKeyboardButton(f"💡 {to_smallcaps('Preset Examples')}", callback_data="caption_examples")])

            await query.message.edit_text(
                f"⚙️ **{to_smallcaps(name + ' Settings')}**\n\n{to_smallcaps('Choose an action below:')}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes specific action callbacks (View, Set, Delete, F-Sub check)."""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "check_fsub":
        if await is_user_subscribed(context.bot, user_id):
            await query.answer(f"✅ {to_smallcaps('Verification successful!')} Welcome.", show_alert=False)
            await show_main_menu(update, context)
        else:
            await query.answer(f"❌ {to_smallcaps('You still haven’t joined both channels!')}", show_alert=True)
            
    elif data == "main_menu":
        USER_STATES.pop(user_id, None)
        await show_main_menu(update, context)
        
    elif data == "open_settings":
        USER_STATES.pop(user_id, None)
        await settings_menu_callback(update, context)
        
    elif data.startswith("view_"):
        key = data.split("_", 1)[1]
        settings = await db.get_user_settings(user_id) or {}
        val = settings.get(key)
        
        if not val:
            await query.answer(f"❌ {to_smallcaps('No custom ' + key.replace('_', ' ') + ' found!')}", show_alert=True)
            return
            
        if key == "thumbnail":
            await query.answer()
            await context.bot.send_photo(chat_id=user_id, photo=val, caption=f"🖼️ {to_smallcaps('Your saved permanent thumbnail:')}")
        else:
            await query.answer()
            await query.message.reply_text(f"👁️ **{to_smallcaps('Your ' + key.replace('_', ' '))}:**\n\n{val}", parse_mode="Markdown")
            
    elif data.startswith("del_"):
        key = data.split("_", 1)[1]
        await db.delete_setting(user_id, key)
        await query.answer(f"🗑️ {to_smallcaps('Successfully deleted ' + key.replace('_', ' ') + '!')}", show_alert=False)
        query.data = f"menu_{key}"
        await sub_menu_handler(update, context)
        
    elif data.startswith("set_"):
        key = data.split("_", 1)[1]
        USER_STATES[user_id] = f"awaiting_{key}"
        await query.answer()
        
        prompts = {
            "thumbnail": f"🖼️ {to_smallcaps('Send the image you want to use as your permanent thumbnail.')}",
            "caption": f"📝 {to_smallcaps('Send your custom caption text.')}\n\n{to_smallcaps('Tags available:')} `{{title}}`, `{{artist}}`, `{{size}}`",
            "audio_title": f"🎵 {to_smallcaps('Send your custom audio title/header text.')}",
            "artist_name": f"🎙️ {to_smallcaps('Send your custom artist name.')}"
        }
        
        keyboard = [[InlineKeyboardButton(f"🔙 {to_smallcaps('Cancel')}", callback_data=f"menu_{key}")]]
        await query.message.edit_text(prompts.get(key, to_smallcaps("Send your value:")), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "caption_examples":
        await query.answer()
        example_text = (
            f"💡 **{to_smallcaps('Caption Preset Examples')}**\n\n"
            f"1️⃣ {to_smallcaps('Minimal & Channel Link')}:\n"
            "`🎵 {title} - {artist} [{size}]\n📢 Join: @YourChannel`\n\n"
            f"2️⃣ {to_smallcaps('Structured Audio Layout')}:\n"
            "`🎧 Track: {title}\n👤 Artist: {artist}\n📊 Size: {size}\n\n⚡ Uploaded via @YourChannel`"
        )
        keyboard = [[InlineKeyboardButton(f"🔙 {to_smallcaps('Back to Caption')}", callback_data="menu_caption")]]
        await query.message.edit_text(example_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "about_menu":
        await query.answer()
        text = (
            f"ℹ️ **{to_smallcaps('About Bot')}**\n\n"
            f"• **{to_smallcaps('Developer/Owner')}:** {Config.OWNER_USERNAME}\n"
            f"• **{to_smallcaps('Theme')}:** Deadpool Audio Renamer\n\n"
            f"{to_smallcaps('High-performance audio renaming bot built with clean modular architecture.')}"
        )
        keyboard = [
            [
                InlineKeyboardButton(f"📢 {to_smallcaps('Updates')}", url=Config.UPDATE_CHANNEL),
                InlineKeyboardButton(f"💬 {to_smallcaps('Support')}", url=Config.SUPPORT_GROUP)
            ],
            [
                InlineKeyboardButton(f"💻 {to_smallcaps('Source Code')}", url="https://github.com/MrBoss002/Audio-Renamer"),
                InlineKeyboardButton(f"🔙 {to_smallcaps('Main Menu')}", callback_data="main_menu")
            ]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def text_and_media_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captures user input when setting thumbnails, captions, or custom titles/artists."""
    user_id = update.effective_user.id
    state = USER_STATES.get(user_id)
    
    if not state:
        return

    if state == "awaiting_thumbnail":
        if not update.message.photo:
            await update.message.reply_text(f"❌ {to_smallcaps('Please send a valid image for your thumbnail.')}")
            return
        file_id = update.message.photo[-1].file_id
        await db.update_setting(user_id, "thumbnail", file_id)
        USER_STATES.pop(user_id, None)
        await update.message.reply_text(f"✅ {to_smallcaps('Permanent thumbnail saved successfully!')}")
        
    elif state in ["awaiting_caption", "awaiting_audio_title", "awaiting_artist_name"]:
        if not update.message.text:
            await update.message.reply_text(f"❌ {to_smallcaps('Please send valid text.')}")
            return
        
        key_map = {
            "awaiting_caption": "caption",
            "awaiting_audio_title": "audio_title",
            "awaiting_artist_name": "artist_name"
        }
        db_key = key_map.get(state)
        val = update.message.text
        
        try:
            await db.update_setting(user_id, db_key, val)
            USER_STATES.pop(user_id, None)
            await update.message.reply_text(f"✅ {to_smallcaps('Successfully updated your ' + db_key.replace('_', ' ') + '!')}")
        except Exception as e:
            logger.error(f"Failed to update setting {db_key} for user {user_id}: {e}")
            await update.message.reply_text(f"❌ {to_smallcaps('Failed to save. Please try again.')}")
            return

    settings = await db.get_user_settings(user_id) or {}
    
    thumb_status = f"✅ {to_smallcaps('Set')}" if settings.get("thumbnail") else f"❌ {to_smallcaps('Not Set')}"
    caption_status = f"`{settings.get('caption')}`" if settings.get("caption") else f"❌ {to_smallcaps('Not Set')}"
    title_status = f"`{settings.get('audio_title')}`" if settings.get("audio_title") else f"❌ {to_smallcaps('Not Set')}"
    artist_status = f"`{settings.get('artist_name')}`" if settings.get("artist_name") else f"❌ {to_smallcaps('Not Set')}"

    text = (
        f"⚙️ **{to_smallcaps('User Settings Dashboard')}**\n\n"
        f"👤 **{to_smallcaps('User ID')}:** `{user_id}`\n"
        f"🖼️ **{to_smallcaps('Permanent Thumbnail')}:** {thumb_status}\n"
        f"📝 **{to_smallcaps('Custom Caption')}:** {caption_status}\n"
        f"🎵 **{to_smallcaps('Audio Title/Header')}:** {title_status}\n"
        f"🎙️ **{to_smallcaps('Artist Name')}:** {artist_status}\n\n"
        f"{to_smallcaps('Select another category below to customize:')}"
    )
    
    keyboard = [
        [
            InlineKeyboardButton(f"🖼️ {to_smallcaps('Thumbnail')}", callback_data="menu_thumb"),
            InlineKeyboardButton(f"📝 {to_smallcaps('Caption')}", callback_data="menu_caption")
        ],
        [
            InlineKeyboardButton(f"🎵 {to_smallcaps('Audio Title')}", callback_data="menu_title"),
            InlineKeyboardButton(f"🎙️ {to_smallcaps('Artist')}", callback_data="menu_artist")
        ],
        [InlineKeyboardButton(f"🔙 {to_smallcaps('Main Menu')}", callback_data="main_menu")]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_audio_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming audio files specifically, applying custom title, artist, thumbnail, and caption."""
    user_id = update.effective_user.id
    
    if user_id in USER_STATES:
        return

    message = update.message
    audio = message.audio
    
    if not audio:
        return

    if not await is_user_subscribed(context.bot, user_id):
        await send_fsub_message(update, context)
        return

    settings = await db.get_user_settings(user_id) or {}
    
    original_name = getattr(audio, "file_name", "audio_file.mp3")
    file_size_bytes = getattr(audio, "file_size", 0)
    
    if file_size_bytes > 1024 * 1024:
        size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
    else:
        size_str = f"{file_size_bytes / 1024:.2f} KB"

    base_name = os.path.splitext(original_name)[0]
    custom_title = settings.get("audio_title") or base_name
    custom_artist = settings.get("artist_name") or "Unknown Artist"
    
    raw_caption = settings.get("caption")
    if raw_caption:
        try:
            caption = raw_caption.format(
                title=custom_title,
                artist=custom_artist,
                size=size_str
            )
        except Exception:
            caption = f"🎵 {custom_title} - {custom_artist} [{size_str}]\n\nvia : @BossAudioRenamerBot 🎊"
    else:
        caption = f"🎵 **Title:** {custom_title}\n🎙️ **Artist:** {custom_artist}\n📊 **Size:** {size_str}\n\nvia : @BossAudioRenamerBot 🎊"

    status_msg = await message.reply_text(f"📥 {to_smallcaps('Downloading and processing your audio file...')}")

    try:
        file = await context.bot.get_file(audio.file_id)
        file_path = f"downloads_{user_id}_{original_name}"
        await file.download_to_drive(file_path)

        thumbnail = settings.get("thumbnail")

        with open(file_path, 'rb') as audio_file:
            await context.bot.send_audio(
                chat_id=user_id,
                audio=audio_file,
                title=custom_title,
                performer=custom_artist,
                caption=caption,
                parse_mode="Markdown",
                thumbnail=thumbnail if thumbnail else None
            )

        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error processing audio file for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Error processing file: `{e}`", parse_mode="Markdown")

def run_dummy_server():
    """Starts a minimal HTTP server to satisfy Render's port-binding check."""
    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Deadpool Audio Renamer Bot is alive and running!")
            
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

def main():
    """Application Entrypoint."""
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN is missing from environment variables!")
        return

    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(sub_menu_handler, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), text_and_media_input_handler))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio_file))

    logger.info("Deadpool Audio Renamer Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
