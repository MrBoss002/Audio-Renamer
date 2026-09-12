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

# Temporary state tracker for setting custom values (thumbnails, captions, etc.)
USER_STATES = {}

async def is_user_subscribed(bot, user_id: int) -> bool:
    """Checks if the user is a member of both mandatory F-Sub channels."""
    if not Config.CHANNEL_1_ID or not Config.CHANNEL_2_ID:
        return True  # Bypass if IDs are not configured
        
    for channel_id in [Config.CHANNEL_1_ID, Config.CHANNEL_2_ID]:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
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
        "⚠️ **Access Restricted**\n\n"
        "To use this bot, you must join both of our official channels. "
        "Please join using the buttons below and click **Try Again**."
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
        [InlineKeyboardButton("⚙️ Settings Hub", callback_data="open_settings")],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about_menu"),
            InlineKeyboardButton("📢 Updates", url=Config.UPDATE_CHANNEL)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🔥 **Welcome to Deadpool Audio/Video Renamer!**\n\n"
        "I can help you rename files, inject metadata, customize thumbnails, "
        "and apply personal captions automatically.\n\n"
        "Choose an option below to manage your preferences:"
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
    
    settings = await db.get_user_settings(user_id)
    
    thumb_status = "✅ Set" if settings["thumbnail"] else "❌ Not Set"
    caption_status = f"`{settings['caption']}`" if settings["caption"] else "❌ Not Set"
    title_status = f"`{settings['audio_title']}`" if settings["audio_title"] else "❌ Not Set"
    artist_status = f"`{settings['artist_name']}`" if settings["artist_name"] else "❌ Not Set"

    text = (
        "⚙️ **USER SETTINGS DASHBOARD**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"🖼️ **Permanent Thumbnail:** {thumb_status}\n"
        f"📝 **Custom Caption:** {caption_status}\n"
        f"🎵 **Audio Title/Header:** {title_status}\n"
        f"🎙️ **Artist Name:** {artist_status}\n\n"
        "Select a category below to configure:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🖼️ Thumbnail", callback_data="menu_thumb"),
            InlineKeyboardButton("📝 Caption", callback_data="menu_caption")
        ],
        [
            InlineKeyboardButton("🎵 Audio Title", callback_data="menu_title"),
            InlineKeyboardButton("🎙️ Artist", callback_data="menu_artist")
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
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
                    InlineKeyboardButton("📤 Set", callback_data=f"set_{key}"),
                    InlineKeyboardButton("👁️ View", callback_data=f"view_{key}")
                ],
                [
                    InlineKeyboardButton("🗑️ Delete", callback_data=f"del_{key}"),
                    InlineKeyboardButton("🔙 Settings", callback_data="open_settings")
                ]
            ]
            if key == "caption":
                keyboard.insert(1, [InlineKeyboardButton("💡 Preset Examples", callback_data="caption_examples")])

            await query.message.edit_text(
                f"⚙️ **{name} Settings**\n\nChoose an action below:",
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
            await query.answer("✅ Verification successful! Welcome.", show_alert=False)
            await show_main_menu(update, context)
        else:
            await query.answer("❌ You still haven't joined both channels!", show_alert=True)
            
    elif data == "main_menu":
        USER_STATES.pop(user_id, None)
        await show_main_menu(update, context)
        
    elif data == "open_settings":
        USER_STATES.pop(user_id, None)
        await settings_menu_callback(update, context)
        
    elif data.startswith("view_"):
        key = data.split("_")[1]
        settings = await db.get_user_settings(user_id)
        val = settings.get(key)
        
        if not val:
            await query.answer(f"❌ No custom {key.replace('_', ' ')} found!", show_alert=True)
            return
            
        if key == "thumbnail":
            await query.answer()
            await context.bot.send_photo(chat_id=user_id, photo=val, caption="🖼️ Your saved permanent thumbnail:")
        else:
            await query.answer()
            await query.message.reply_text(f"👁️ **Your {key.replace('_', ' ')}:**\n\n{val}", parse_mode="Markdown")
            
    elif data.startswith("del_"):
        key = data.split("_")[1]
        await db.delete_setting(user_id, key)
        await query.answer(f"🗑️ Successfully deleted {key.replace('_', ' ')}!", show_alert=False)
        query.data = f"menu_{key}"
        await sub_menu_handler(update, context)
        
    elif data.startswith("set_"):
        key = data.split("_")[1]
        USER_STATES[user_id] = f"awaiting_{key}"
        await query.answer()
        
        prompts = {
            "thumbnail": "🖼️ Send the image you want to use as your permanent thumbnail.",
            "caption": "📝 Send your custom caption text.\n\nTags available: `{title}`, `{artist}`, `{size}`",
            "audio_title": "🎵 Send your custom audio title/header text.",
            "artist_name": "🎙️ Send your custom artist name."
        }
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data=f"menu_{key}")]]
        await query.message.edit_text(prompts.get(key, "Send your value:"), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "caption_examples":
        await query.answer()
        example_text = (
            "💡 **CAPTION PRESET EXAMPLES**\n\n"
            "1️⃣ Minimal & Channel Link:\n"
            "`🎵 {title} - {artist} [{size}]\n📢 Join: @YourChannel`\n\n"
            "2️⃣ Structured Audio Layout:\n"
            "`🎧 Track: {title}\n👤 Artist: {artist}\n📊 Size: {size}\n\n⚡ Uploaded via @YourChannel`"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back to Caption", callback_data="menu_caption")]]
        await query.message.edit_text(example_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "about_menu":
        await query.answer()
        text = (
            "ℹ️ **ABOUT BOT**\n\n"
            f"• **Developer/Owner:** {Config.OWNER_USERNAME}\n"
            f"• **Theme:** Deadpool Audio/Video Renamer\n\n"
            "High-performance renaming bot built with clean modular architecture."
        )
        keyboard = [
            [
                InlineKeyboardButton("📢 Updates", url=Config.UPDATE_CHANNEL),
                InlineKeyboardButton("💬 Support", url=Config.SUPPORT_GROUP)
            ],
            [
                InlineKeyboardButton("💻 Source Code", url="https://github.com/MrBoss002/Audio-Renamer"),
                InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")
            ]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def text_and_media_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captures user input when setting thumbnails, captions, or custom titles and refreshes the settings dashboard."""
    user_id = update.effective_user.id
    state = USER_STATES.get(user_id)
    
    if not state:
        return

    if state == "awaiting_thumbnail":
        if not update.message.photo:
            await update.message.reply_text("❌ Please send a valid **image** for your thumbnail.")
            return
        file_id = update.message.photo[-1].file_id
        await db.update_setting(user_id, "thumbnail", file_id)
        USER_STATES.pop(user_id, None)
        await update.message.reply_text("✅ Permanent thumbnail saved successfully!")
        
    elif state in ["awaiting_caption", "awaiting_audio_title", "awaiting_artist_name"]:
        if not update.message.text:
            await update.message.reply_text("❌ Please send valid **text**.")
            return
        
        key_map = {
            "awaiting_caption": "caption",
            "awaiting_audio_title": "audio_title",
            "awaiting_artist_name": "artist_name"
        }
        db_key = key_map[state]
        val = update.message.text
        
        await db.update_setting(user_id, db_key, val)
        USER_STATES.pop(user_id, None)
        await update.message.reply_text(f"✅ Successfully updated your {db_key.replace('_', ' ')}!")

    settings = await db.get_user_settings(user_id)
    
    thumb_status = "✅ Set" if settings["thumbnail"] else "❌ Not Set"
    caption_status = f"`{settings['caption']}`" if settings["caption"] else "❌ Not Set"
    title_status = f"`{settings['audio_title']}`" if settings["audio_title"] else "❌ Not Set"
    artist_status = f"`{settings['artist_name']}`" if settings["artist_name"] else "❌ Not Set"

    text = (
        "⚙️ **USER SETTINGS DASHBOARD**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"🖼️ **Permanent Thumbnail:** {thumb_status}\n"
        f"📝 **Custom Caption:** {caption_status}\n"
        f"🎵 **Audio Title/Header:** {title_status}\n"
        f"🎙️ **Artist Name:** {artist_status}\n\n"
        "Select another category below to customize:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🖼️ Thumbnail", callback_data="menu_thumb"),
            InlineKeyboardButton("📝 Caption", callback_data="menu_caption")
        ],
        [
            InlineKeyboardButton("🎵 Audio Title", callback_data="menu_title"),
            InlineKeyboardButton("🎙️ Artist", callback_data="menu_artist")
        ],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def run_dummy_server():
    """Starts a minimal HTTP server to satisfy Render's port-binding check."""
    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Deadpool Renamer Bot is alive and running!")
            
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

def main():
    """Application Entrypoint."""
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN is missing from environment variables!")
        return

    # Start the dummy HTTP server in a daemon thread for Render web service compatibility
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(sub_menu_handler, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), text_and_media_input_handler))

    logger.info("Deadpool Audio Renamer Bot is up and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
