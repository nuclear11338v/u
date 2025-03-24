import asyncio
from pyrogram import Client, filters
import google.generativeai as genai
import hashlib
import sys
import sqlite3
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
BOT_TOKEN = "7690937386:AAG5BY6X4nzbz0jmtAWxVYWsFSFxW7tV6IE"
API_ID = 27152769
API_HASH = "b98dff566803b43b3c3120eec537fc1d"
GEMINI_API_KEY = "AIzaSyCLWwTnaGsnwqIPtaz1FP2AnNwS86trVeY"
OWNER_ID = 8181395757
MAX_FREE_USERS = 100

# Gemini AI Configuration
genai.configure(api_key=GEMINI_API_KEY)
text_model = genai.GenerativeModel("gemini-1.5-pro")
vision_model = genai.GenerativeModel("gemini-1.5-pro-vision")

# Initialize Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database Setup
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY,
              username TEXT,
              is_premium INTEGER DEFAULT 0,
              referral_count INTEGER DEFAULT 0,
              referred_by INTEGER,
              is_banned INTEGER DEFAULT 0)''')
conn.commit()

def stylize_text(text):
    mapping = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ',
        'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
        'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    }
    return ''.join(mapping.get(c, c) for c in text)

async def get_gemini_response(prompt, image=None):
    try:
        if image:
            response = vision_model.generate_content([prompt, image])
        else:
            response = text_model.generate_content(prompt)
        return response.text if response.text else "ɴᴏ ʀᴇsᴘᴏɴsᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ."
    except Exception as e:
        return f"ᴇʀʀᴏʀ: {str(e)}"

@app.on_message(filters.command("start"))
async def start_command(client, message):
    args = message.text.split()
    referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    
    user_id = message.from_user.id
    username = message.from_user.username
    
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    if c.fetchone():
        c.execute('UPDATE users SET username = ? WHERE user_id = ?', (username, user_id))
        conn.commit()
        await message.reply("ʜᴇʏ ᴛʜᴇʀᴇ ᴡᴇʟᴄᴏᴍᴇ!\n\nɪ'ᴍ ᴛᴇᴀᴍ x ɢᴘᴛ\nʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ?\n\nᴛʏᴘᴇ /ʜᴇʟᴘ ᴛᴏ sᴇᴇ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ!", disable_web_page_preview=True)
        return

    c.execute('SELECT COUNT(*) FROM users WHERE is_premium = 0')
    free_users = c.fetchone()[0]
    
    if referrer_id:
        c.execute('SELECT is_premium FROM users WHERE user_id = ?', (referrer_id,))
        referrer_status = c.fetchone()
        premium_referral = referrer_status and referrer_status[0] == 1
    else:
        premium_referral = False

    if free_users >= MAX_FREE_USERS and not premium_referral:
        await message.reply("ᴜsᴇʀ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ. ɢᴇᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ's ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ ᴛᴏ ᴊᴏɪɴ!", disable_web_page_preview=True)
        return

    c.execute('INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)',
              (user_id, username, referrer_id))
    if referrer_id:
        c.execute('UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?', (referrer_id,))
        c.execute('SELECT referral_count FROM users WHERE user_id = ?', (referrer_id,))
        new_count = c.fetchone()[0]
        if new_count >= 5:
            c.execute('UPDATE users SET is_premium = 1 WHERE user_id = ?', (referrer_id,))
            await client.send_message(referrer_id, "ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs\n\nᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴄʜᴏᴏsɪɴɢ ᴍᴇ!\nɪ ʜᴏᴘᴇ ʏᴏᴜ ᴇɴᴊᴏʏ", disable_web_page_preview=True)
    conn.commit()

    referral_link = f"https://t.me/{(await client.get_me()).username}?start={user_id}"
    welcome_msg = f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {stylize_text('Gemini AI Pro')}!\n\nᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs: {('ᴀᴄᴛɪᴠᴇ' if premium_referral else 'ʙᴀsɪᴄ')}\nʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ: {referral_link}\nsᴜᴘᴘᴏʀᴛ: https://t.me/TEAM_X_OG\nᴘᴏᴡᴇʀᴇᴅ ʙʏ: https://t.me/PB_X01\n\nᴜsᴇ /ʜᴇʟᴘ ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs"
    await message.reply(welcome_msg, disable_web_page_preview=True)

@app.on_message(filters.command("referral"))
async def referral_command(client, message):
    user_id = message.from_user.id
    c.execute('SELECT referral_count, is_premium, referred_by FROM users WHERE user_id = ?', (user_id,))
    user_data = c.fetchone()
    
    if user_data:
        count, premium, referred_by = user_data
        link = f"https://t.me/{(await client.get_me()).username}?start={user_id}"
        
        if referred_by:
            c.execute('SELECT username FROM users WHERE user_id = ?', (referred_by,))
            referrer = c.fetchone()
            referrer_text = f"ʀᴇғᴇʀʀᴇᴅ ʙʏ: @{referrer[0]}" if referrer else "ʀᴇғᴇʀʀᴇᴅ ʙʏ: ɴᴏɴᴇ"
        else:
            referrer_text = "ʀᴇғᴇʀʀᴇᴅ ʙʏ: ɴᴏɴᴇ"
        
        c.execute('SELECT username FROM users WHERE referred_by = ?', (user_id,))
        referred_users = c.fetchall()
        referred_text = ""
        if referred_users:
            referred_text += "ʀᴇғᴇʀʀᴇᴅ ᴜsᴇʀs:\n"
            for user in referred_users:
                referred_text += f"@{user[0]}\n"
        
        response = f"{stylize_text('Your Referral Stats')}:\n\nʏᴏᴜʀ ʟɪɴᴋ: {link}\nᴛᴏᴛᴀʟ ʀᴇғᴇʀʀᴀʟs: {count}\nᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs: {'ᴀᴄᴛɪᴠᴇ' if premium else 'ɪɴᴀᴄᴛɪᴠᴇ'}\nsᴜᴘᴘᴏʀᴛ: https://t.me/TEAM_X_OG\nᴘᴏᴡᴇʀᴇᴅ ʙʏ: https://t.me/PB_X01\n\nʀᴇғᴇʀʀᴀʟ ᴛʀᴇᴇ:\n{referrer_text}\n{referred_text}"
        await message.reply(response, disable_web_page_preview=True)
    else:
        await message.reply("ғɪʀsᴛ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʙᴏᴛ\n\n/sᴛᴀʀᴛ", disable_web_page_preview=True)

@app.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = f"{stylize_text('Gemini AI Pro Bot Commands')}:\n\n/sᴛᴀʀᴛ - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ ʟɪɴᴋ\n/ʀᴇғᴇʀʀᴀʟ - ᴠɪᴇᴡ ʏᴏᴜʀ ʀᴇғᴇʀʀᴀʟ sᴛᴀᴛs ᴀɴᴅ ᴛʀᴇᴇ\n/ʜᴇʟᴘ - sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ\n/sᴛᴀᴛᴜs - ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴛᴀᴛᴜs ᴀɴᴅ ʀᴇғᴇʀʀᴀʟs\n/ғᴇᴇᴅʙᴀᴄᴋ - sᴇɴᴅ ғᴇᴇᴅʙᴀᴄᴋ ᴛᴏ ᴛʜᴇ ᴏᴡɴᴇʀ\n\nғᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:\nᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ\n\nᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅs:\n/ᴀᴘᴘʀᴏᴠᴇ - ᴀᴘᴘʀᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss\n/ʀᴇᴍᴏᴠᴇ - ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss\n/ᴜsᴇʀs - ʟɪsᴛ ᴀʟʟ ᴜsᴇʀs\n/ʙᴀɴ - ʙᴀɴ ᴀ ᴜsᴇʀ\n/ᴜɴʙᴀɴ - ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ\n/ʙʀᴏᴀᴅᴄᴀsᴛ - sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs\n/sᴛᴀᴛs - sʜᴏᴡ ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs\n\nsᴜᴘᴘᴏʀᴛ: https://t.me/TEAM_X_OG\nᴘᴏᴡᴇʀᴇᴅ ʙʏ: https://t.me/PB_X01\n\nsɪᴍᴘʟʏ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʜᴏᴛᴏ ᴛᴏ ɢᴇᴛ ᴀɪ ʀᴇsᴘᴏɴsᴇs!"
    await message.reply(help_text, disable_web_page_preview=True)

@app.on_message(filters.command("status"))
async def status_command(client, message):
    user_id = message.from_user.id
    c.execute('SELECT is_premium, referral_count FROM users WHERE user_id = ?', (user_id,))
    user_data = c.fetchone()
    if user_data:
        premium, referrals = user_data
        status_text = "ᴘʀᴇᴍɪᴜᴍ" if premium else "ʙᴀsɪᴄ"
        response = f"{stylize_text('Your Status')}:\n\nsᴛᴀᴛᴜs: {status_text}\nʀᴇғᴇʀʀᴀʟs: {referrals}\n\nʀᴇғᴇʀ ₅ ᴜsᴇʀs ᴛᴏ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ!\nsᴜᴘᴘᴏʀᴛ: https://t.me/TEAM_X_OG\nᴘᴏᴡᴇʀᴇᴅ ʙʏ: https://t.me/PB_X01"
        await message.reply(response, disable_web_page_preview=True)
    else:
        await message.reply("ғɪʀsᴛ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʙᴏᴛ\n\n/sᴛᴀʀᴛ", disable_web_page_preview=True)

@app.on_message(filters.command("feedback"))
async def feedback_command(client, message):
    user_id = message.from_user.id
    try:
        feedback_text = message.text.split(maxsplit=1)[1]
        user_tag = f"@{message.from_user.username}" if message.from_user.username else f"ɪᴅ: {user_id}"
        owner_msg = f"ғᴇᴇᴅʙᴀᴄᴋ ғʀᴏᴍ {user_tag}:\n{feedback_text}"
        await client.send_message(OWNER_ID, owner_msg, disable_web_page_preview=True)
        await message.reply("sᴜᴄᴄᴇss", disable_web_page_preview=True)
    except:
        await message.reply("ᴜsᴀɢᴇ: /ғᴇᴇᴅʙᴀᴄᴋ <ᴍᴇssᴀɢᴇ>", disable_web_page_preview=True)

@app.on_message(filters.command("approve") & filters.user(OWNER_ID))
async def approve_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_premium = 1 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"ᴜsᴇʀ {target_id} ᴀᴘᴘʀᴏᴠᴇᴅ ᴀs ᴘʀᴇᴍɪᴜᴍ!", disable_web_page_preview=True)
    except:
        await message.reply("ᴜsᴀɢᴇ: /ᴀᴘᴘʀᴏᴠᴇ <ᴜsᴇʀ_ɪᴅ>", disable_web_page_preview=True)

@app.on_message(filters.command("remove") & filters.user(OWNER_ID))
async def remove_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"ᴜsᴇʀ {target_id} ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʀᴇᴍᴏᴠᴇᴅ!", disable_web_page_preview=True)
    except:
        await message.reply("ᴜsᴀɢᴇ: /ʀᴇᴍᴏᴠᴇ <ᴜsᴇʀ_ɪᴅ>", disable_web_page_preview=True)

@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def users_command(client, message):
    c.execute('SELECT user_id, username, is_premium, referral_count, is_banned FROM users')
    users = c.fetchall()
    
    response = f"{stylize_text('Registered Users')}:\n\n"
    for user in users:
        response += f"ɪᴅ: {user[0]}\nᴜsᴇʀ: @{user[1]}\nᴘʀᴇᴍɪᴜᴍ: {'ʏᴇs' if user[2] else 'ɴᴏ'}\nʀᴇғᴇʀʀᴀʟs: {user[3]}\nʙᴀɴɴᴇᴅ: {'ʏᴇs' if user[4] else 'ɴᴏ'}\n\n"
    
    for i in range(0, len(response), 4000):
        await message.reply(response[i:i+4000], disable_web_page_preview=True)

@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"ᴜsᴇʀ {target_id} ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.", disable_web_page_preview=True)
    except:
        await message.reply("ᴜsᴀɢᴇ: /ʙᴀɴ <ᴜsᴇʀ_ɪᴅ>", disable_web_page_preview=True)

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"ᴜsᴇʀ {target_id} ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.", disable_web_page_preview=True)
    except:
        await message.reply("ᴜsᴀɢᴇ: /ᴜɴʙᴀɴ <ᴜsᴇʀ_ɪᴅ>", disable_web_page_preview=True)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_command(client, message):
    try:
        broadcast_text = message.text.split(maxsplit=1)[1]
        c.execute('SELECT user_id FROM users')
        users = c.fetchall()
        for user in users:
            try:
                await client.send_message(user[0], broadcast_text, disable_web_page_preview=True)
            except:
                pass
        await message.reply("ʙʀᴏᴀᴅᴄᴀsᴛ sᴇɴᴛ ᴛᴏ ᴀʟʟ ᴜsᴇʀs.", disable_web_page_preview=True)
    except:
        await message.reply("ᴜsᴀɢᴇ: /ʙʀᴏᴀᴅᴄᴀsᴛ <ᴍᴇssᴀɢᴇ>", disable_web_page_preview=True)

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_command(client, message):
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
    premium_users = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1')
    banned_users = c.fetchone()[0]
    response = f"{stylize_text('Bot Statistics')}:\n\nᴛᴏᴛᴀʟ ᴜsᴇʀs: {total_users}\nᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: {premium_users}\nʙᴀɴɴᴇᴅ ᴜsᴇʀs: {banned_users}"
    await message.reply(response, disable_web_page_preview=True)

@app.on_message(filters.text | filters.photo)
async def handle_messages(client, message):
    user_id = message.from_user.id
    username = message.from_user.username
    c.execute('UPDATE users SET username = ? WHERE user_id = ?', (username, user_id))
    conn.commit()
    
    await client.send_chat_action(user_id, "typing")
    
    c.execute('SELECT is_premium, is_banned FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        await message.reply("ғɪʀsᴛ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ʙᴏᴛ\n\n/sᴛᴀʀᴛ", disable_web_page_preview=True)
        return
    if user[1]:
        await message.reply("ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴛʜɪs ʙᴏᴛ. ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴜs: @ᴘʙ_x₀₁", disable_web_page_preview=True)
        return
    
    prompt = message.text or message.caption
    image = None
    
    if message.photo:
        try:
            file_path = await client.download_media(message.photo.file_id)
            with open(file_path, 'rb') as f:
                image = f.read()
        except Exception as e:
            await message.reply(f"ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ: {str(e)}", disable_web_page_preview=True)
            return

    processing_msg = await message.reply("ᴘʀᴏᴄᴇssɪɴɢ", disable_web_page_preview=True)
    response = await get_gemini_response(prompt, image)
    await processing_msg.delete()

    await message.reply(response, disable_web_page_preview=True)

    user_tag = f"@{message.from_user.username}" if message.from_user.username else f"ɪᴅ: {user_id}"
    owner_msg = f"ɴᴇᴡ ʀᴇǫᴜᴇsᴛ ғʀᴏᴍ {user_tag}\nǫᴜᴇʀʏ: {prompt[:100]}..."
    await client.send_message(OWNER_ID, owner_msg, disable_web_page_preview=True)

print("ʙᴏᴛ ɪs ʀᴜɴɴɪɴɢ...")
app.run()