import asyncio
from pyrogram import Client, filters
import google.generativeai as genai
import hashlib
import sys
import sqlite3
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configuration
BOT_TOKEN = "7690937386:AAG5BY6X4nzbz0jmtAWxVYWsFSFxW7tV6IE"
API_ID = 27152769  # Get this from my.telegram.org
API_HASH = "b98dff566803b43b3c3120eec537fc1d"  # Get this from my.telegram.org
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
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    }
    return ''.join(mapping.get(c.lower(), c) for c in text)

async def get_gemini_response(prompt, image=None):
    try:
        if image:
            response = vision_model.generate_content([prompt, image])
        else:
            response = text_model.generate_content(prompt)
        return response.text if response.text else "No response generated."
    except Exception as e:
        return f"Error: {str(e)}"

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
        await message.reply("𝗛𝗘𝗬 𝗧𝗛𝗘𝗥𝗘 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 !\n\nI'м Tᴇᴀм x Gᴘт 🌟\nHow Cᴀɴ ι Hᴇʟᴘ You ?\n\nTʏᴘᴇ /help To Sᴇᴇ How To Usᴇ Mᴇ !", disable_web_page_preview=True)
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
        await message.reply("Usᴇʀ Lιмιт Rᴇᴀcнᴇᴅ. Gᴇт ᴀ Pʀᴇмιuм Usᴇʀ's Rᴇғᴇʀʀᴀʟ Lιɴκ To Joιɴ!", disable_web_page_preview=True)
        return

    c.execute('INSERT INTO users (user_id, username, referred_by) VALUES (?, ?, ?)',
              (user_id, username, referrer_id))
    if referrer_id:
        c.execute('UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?', (referrer_id,))
        c.execute('SELECT referral_count FROM users WHERE user_id = ?', (referrer_id,))
        new_count = c.fetchone()[0]
        if new_count >= 5:
            c.execute('UPDATE users SET is_premium = 1 WHERE user_id = ?', (referrer_id,))
            await client.send_message(referrer_id, "🎊 𝗖𝗢𝗡𝗚𝗥𝗔𝗧𝗨𝗟𝗔𝗧𝗜𝗢𝗡𝗦 🎊\n\nTнᴀɴκ You Foʀ Cнoosιɴԍ Mᴇ !\nι нoᴘᴇ ʏouʀ ιɴנoʏιɴԍ 🌟👀🥳", disable_web_page_preview=True)
    conn.commit()

    referral_link = f"https://t.me/{(await client.get_me()).username}?start={user_id}"
    welcome_msg = f"""**🤖 Welcome to {stylize_text('Gemini AI Pro')}!**

🎖️ *Premium Status*: {'Active 🎖️' if premium_referral else 'Basic'}
*Toтᴀʟ Rᴇғᴇʀʀᴀʟs*: [Click Here]({referral_link})
🎯 Referrals Count: [implementing]

Suᴘᴘoʀт: [TEAM X OG](https://t.me/TEAM_X_OG)
Powᴇʀᴇᴅ Bʏ: [PB_X01](https://t.me/PB_X01)

Use /help for commands"""
    await message.reply(welcome_msg, parse_mode="markdown", disable_web_page_preview=True)

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
            referrer_text = f"└── Referred by: @{referrer[0]}" if referrer else "└── Referred by: None"
        else:
            referrer_text = "└── Referred by: None"
        
        c.execute('SELECT username FROM users WHERE referred_by = ?', (user_id,))
        referred_users = c.fetchall()
        referred_text = ""
        if referred_users:
            referred_text += "    ├── Referred users:\n"
            for i, user in enumerate(referred_users):
                if i == len(referred_users) - 1:
                    referred_text += f"    └── @{user[0]}\n"
                else:
                    referred_text += f"    ├── @{user[0]}\n"
        
        response = f"""**📊 {stylize_text('Your Referral Stats')}:**

🔗 *Your Link*: [Click Here]({link})
👥 *Total Referrals*: {count}
🎖️ *Premium Status*: {'Active' if premium else 'Inactive'}

Support: [TEAM X OG](https://t.me/TEAM_X_OG)
Powered By: [PB_X01](https://t.me/PB_X01)

**Referral Tree:**
```
{referrer_text}
{referred_text}
```"""
        await message.reply(response, parse_mode="markdown", disable_web_page_preview=True)
    else:
        await message.reply("First Start The Bot Then You Can Use This Bot\n\n/start", disable_web_page_preview=True)

@app.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = f"""**🤖 {stylize_text('Gemini AI Pro Bot Commands')}:**

🌟 /start - Start The Bot And Get Your Referral Link
📊 /referral - View Your Referral Stats And Tree
❓ /help - Show This Help Message
📈 /status - Check Your Status And Referrals
💬 /feedback - Send Feedback To The Owner

For Premium Users:
🎖️ Premium Features Are Available Automatically

Owner Commands:
👑 /approve - Approve Premium Access
🚫 /remove - Remove Premium Access
📋 /users - List All users
🚫 /ban - Ban a User
✅ /unban - Unban a User
📢 /broadcast - Send a Message To All Users
📊 /stats - Show Bot Statistics

Support: [TEAM X OG](https://t.me/TEAM_X_OG)
Powered By: [PB_X01](https://t.me/PB_X01)

💬 Simply Send a Message Or Photo To Get AI Responses!"""
    await message.reply(help_text, parse_mode="markdown", disable_web_page_preview=True)

@app.on_message(filters.command("status"))
async def status_command(client, message):
    user_id = message.from_user.id
    c.execute('SELECT is_premium, referral_count FROM users WHERE user_id = ?', (user_id,))
    user_data = c.fetchone()
    if user_data:
        premium, referrals = user_data
        status_text = "🎖️ Premium" if premium else "🆓 Basic"
        response = f"""**📊 {stylize_text('Your Status')}:**

🔑 Status: {status_text}
👥 Referrals: {referrals}

Refer 5 Users to Get Premium!

Support: [TEAM X OG](https://t.me/TEAM_X_OG)
Powered By: [PB_X01](https://t.me/PB_X01)"""
        await message.reply(response, parse_mode="markdown", disable_web_page_preview=True)
    else:
        await message.reply("First Start The Bot Then You Can Use This Bot\n\n/start", disable_web_page_preview=True)

@app.on_message(filters.command("feedback"))
async def feedback_command(client, message):
    user_id = message.from_user.id
    try:
        feedback_text = message.text.split(maxsplit=1)[1]
        user_tag = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
        owner_msg = f"**📝 Feedback from {user_tag}:**\n{feedback_text}"
        await client.send_message(OWNER_ID, owner_msg, parse_mode="markdown", disable_web_page_preview=True)
        await message.reply("✅", disable_web_page_preview=True)
    except:
        await message.reply("𝗨𝘀𝗮𝗴𝗲: /𝗳𝗲𝗲𝗱𝗯𝗮𝗰𝗸 <𝗺𝗲𝘀𝘀𝗮𝗴𝗲>", disable_web_page_preview=True)

# Admin Commands
@app.on_message(filters.command("approve") & filters.user(OWNER_ID))
async def approve_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_premium = 1 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"✅ User {target_id} approved as premium!", disable_web_page_preview=True)
    except:
        await message.reply("❌ Usage: /approve <user_id>", disable_web_page_preview=True)

@app.on_message(filters.command("remove") & filters.user(OWNER_ID))
async def remove_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"✅ User {target_id} premium access removed!", disable_web_page_preview=True)
    except:
        await message.reply("❌ Usage: /remove <user_id>", disable_web_page_preview=True)

@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def users_command(client, message):
    c.execute('SELECT user_id, username, is_premium, referral_count, is_banned FROM users')
    users = c.fetchall()
    
    response = f"**📊 {stylize_text('Registered Users')}:**\n\n"
    for user in users:
        response += f"ID: {user[0]}\nUser: @{user[1]}\nPremium: {'✅' if user[2] else '❌'}\nReferrals: {user[3]}\nBanned: {'✅' if user[4] else '❌'}\n\n"
    
    for i in range(0, len(response), 4000):  # Pyrogram has a 4000 character limit
        await message.reply(response[i:i+4000], parse_mode="markdown", disable_web_page_preview=True)

@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"✅ User {target_id} has been banned.", disable_web_page_preview=True)
    except:
        await message.reply("❌ Usage: /ban <user_id>", disable_web_page_preview=True)

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_command(client, message):
    try:
        target_id = int(message.text.split()[1])
        c.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (target_id,))
        conn.commit()
        await message.reply(f"✅ User {target_id} has been unbanned.", disable_web_page_preview=True)
    except:
        await message.reply("❌ Usage: /unban <user_id>", disable_web_page_preview=True)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_command(client, message):
    try:
        broadcast_text = message.text.split(maxsplit=1)[1]
        c.execute('SELECT user_id FROM users')
        users = c.fetchall()
        for user in users:
            try:
                await client.send_message(user[0], broadcast_text, parse_mode="markdown", disable_web_page_preview=True)
            except:
                pass
        await message.reply("✅ Broadcast sent to all users.", disable_web_page_preview=True)
    except:
        await message.reply("❌ Usage: /broadcast <message>", disable_web_page_preview=True)

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_command(client, message):
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
    premium_users = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM users WHERE is_banned = 1')
    banned_users = c.fetchone()[0]
    response = f"""**📊 {stylize_text('Bot Statistics')}:**

👥 Total Users: {total_users}
🎖️ Premium Users: {premium_users}
🚫 Banned Users: {banned_users}"""
    await message.reply(response, parse_mode="markdown", disable_web_page_preview=True)

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
        await message.reply("First Start The Bot Then You Can Use This Bot\n\n/start", disable_web_page_preview=True)
        return
    if user[1]:
        await message.reply("You Are Banned From This Bot. If You Think This Is A Mistake Please Contact Us: @PB_X01", disable_web_page_preview=True)
        return
    
    prompt = message.text or message.caption
    image = None
    
    if message.photo:
        try:
            file_path = await client.download_media(message.photo.file_id)
            with open(file_path, 'rb') as f:
                image = f.read()
        except Exception as e:
            await message.reply(f"❌ Error processing image: {str(e)}", disable_web_page_preview=True)
            return

    processing_msg = await message.reply("🔎", disable_web_page_preview=True)
    response = await get_gemini_response(prompt, image)
    await processing_msg.delete()

    parts = response.split('```')
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Text part
            if part.strip():
                await message.reply(f"{part.strip()}", parse_mode="markdown", disable_web_page_preview=True)
        else:  # Code part
            if part.strip():
                await message.reply(f"```\n{part.strip()}\n```", parse_mode="markdown", disable_web_page_preview=True)

    user_tag = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
    owner_msg = f"**📩 New request from {user_tag}**\n🗒️ Query: {prompt[:100]}..."
    await client.send_message(OWNER_ID, owner_msg, parse_mode="markdown", disable_web_page_preview=True)

# Developer credit check
original_text = """THIS FILE IS MADE BY -> @MR_ARMAN_OWNER\nTHIS FILE IS MADE BY -> @MR_ARMAN_OWNER\nTHIS FILE IS MADE BY -> @MR_ARMAN_OWNER\n\nDM TO BUY PAID FILES"""
expected_hash = "dfcb19d1592200db6b5202025e4b67ba6fc43d9dad9e3eb26e2edb3db71b1921"
generated_hash = hashlib.sha256(original_text.encode()).hexdigest()

if generated_hash != expected_hash:
    print("Please don't change the developer name")
    sys.exit(1)
else:
    print(original_text)

# Start the bot
print("Bot is running...")
app.run()