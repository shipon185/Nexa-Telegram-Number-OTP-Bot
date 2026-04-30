import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import time
import threading
import os
import uuid
import html
import re
from datetime import datetime

# --- Telegram Latest Feature Check (CopyTextButton) ---
try:
    from telebot.types import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# --- কনফিগারেশন ---
TOKEN = "8357858284:AAHj25vUzL9UDQW5FB6f894uqjbYLtTAPwg"  
ADMIN_ID = 6716463642
BASE_URL = "http://185.190.142.81"
NEXA_API_KEY = "nxa_95d912571275bd5332f672231badb7696898c269"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "dxa_bot_premium_data_v4.json"

active_polls = {}
user_states = {}
traffic_cooldowns = {} 
data_lock = threading.RLock()

# --- 185+ Country Flags ---
COUNTRY_FLAGS = {
    "afghanistan": "🇦🇫", "albania": "🇦🇱", "algeria": "🇩🇿", "andorra": "🇦🇩",
    "angola": "🇦🇴", "argentina": "🇦🇷", "armenia": "🇦🇲", "australia": "🇦🇺",
    "austria": "🇦🇹", "azerbaijan": "🇦🇿", "bahamas": "🇧🇸", "bahrain": "🇧🇭",
    "bangladesh": "🇧🇩", "barbados": "🇧🇧", "belarus": "🇧🇾", "belgium": "🇧🇪",
    "belize": "🇧🇿", "benin": "🇧🇯", "bhutan": "🇧🇹", "bolivia": "🇧🇴",
    "bosnia": "🇧🇦", "botswana": "🇧🇼", "brazil": "🇧🇷", "brunei": "🇧🇳",
    "bulgaria": "🇧🇬", "burkina faso": "🇧🇫", "burundi": "🇧🇮", "cambodia": "🇰🇭",
    "cameroon": "🇨🇲", "canada": "🇨🇦", "chile": "🇨🇱", "china": "🇨🇳",
    "colombia": "🇨🇴", "congo": "🇨🇬", "costa rica": "🇨🇷", "croatia": "🇭🇷",
    "cuba": "🇨🇺", "cyprus": "🇨🇾", "czech republic": "🇨🇿", "denmark": "🇩🇰",
    "djibouti": "🇩🇯", "dominican republic": "🇩🇴", "ecuador": "🇪🇨", "egypt": "🇪🇬",
    "el salvador": "🇸🇻", "estonia": "🇪🇪", "ethiopia": "🇪🇹", "fiji": "🇫🇯",
    "finland": "🇫🇮", "france": "🇫🇷", "gabon": "🇬🇦", "gambia": "🇬🇲",
    "georgia": "🇬🇪", "germany": "🇩🇪", "ghana": "🇬🇭", "greece": "🇬🇷",
    "guatemala": "🇬🇹", "guinea": "🇬🇳", "haiti": "🇭🇹", "honduras": "🇭🇳",
    "hungary": "🇭🇺", "iceland": "🇮🇸", "india": "🇮🇳", "indonesia": "🇮🇩",
    "iran": "🇮🇷", "iraq": "🇮🇶", "ireland": "🇮🇪", "israel": "🇮🇱",
    "italy": "🇮🇹", "jamaica": "🇯🇲", "japan": "🇯🇵", "jordan": "🇯🇴",
    "kazakhstan": "🇰🇿", "kenya": "🇰🇪", "kuwait": "🇰🇼", "kyrgyzstan": "🇰🇬",
    "laos": "🇱🇦", "latvia": "🇱🇻", "lebanon": "🇱🇧", "libya": "🇱🇾",
    "lithuania": "🇱🇹", "luxembourg": "🇱🇺", "madagascar": "🇲🇬", "malawi": "🇲🇼",
    "malaysia": "🇲🇾", "maldives": "🇲🇻", "mali": "🇲🇱", "malta": "🇲🇹",
    "mauritius": "🇲🇺", "mexico": "🇲🇽", "moldova": "🇲🇩", "mongolia": "🇲🇳",
    "morocco": "🇲🇦", "mozambique": "🇲🇿", "myanmar": "🇲🇲", "namibia": "🇳🇦",
    "nepal": "🇳🇵", "netherlands": "🇳🇱", "new zealand": "🇳🇿", "nicaragua": "🇳🇮",
    "niger": "🇳🇪", "nigeria": "🇳🇬", "norway": "🇳🇴", "oman": "🇴🇲",
    "pakistan": "🇵🇰", "palestine": "🇵🇸", "panama": "🇵🇦", "paraguay": "🇵🇾",
    "peru": "🇵🇪", "philippines": "🇵🇭", "poland": "🇵🇱", "portugal": "🇵🇹",
    "qatar": "🇶🇦", "romania": "🇷🇴", "russia": "🇷🇺", "rwanda": "🇷🇼",
    "saudi arabia": "🇸🇦", "senegal": "🇸🇳", "serbia": "🇷🇸", "singapore": "🇸🇬",
    "slovakia": "🇸🇰", "slovenia": "🇸🇮", "somalia": "🇸🇴", "south africa": "🇿🇦",
    "south korea": "🇰🇷", "spain": "🇪🇸", "sri lanka": "🇱🇰", "sudan": "🇸🇩",
    "sweden": "🇸🇪", "switzerland": "🇨🇭", "syria": "🇸🇾", "taiwan": "🇹🇼",
    "tajikistan": "🇹🇯", "tanzania": "🇹🇿", "thailand": "🇹🇭", "togo": "🇹🇬",
    "tunisia": "🇹🇳", "turkey": "🇹🇷", "uganda": "🇺🇬", "ukraine": "🇺🇦",
    "united arab emirates": "🇦🇪", "united kingdom": "🇬🇧", "united states": "🇺🇸",
    "uruguay": "🇺🇾", "uzbekistan": "🇺🇿", "venezuela": "🇻🇪", "vietnam": "🇻🇳",
    "yemen": "🇾🇪", "zambia": "🇿🇲", "zimbabwe": "🇿🇼",
    "usa": "🇺🇸", "uk": "🇬🇧", "uae": "🇦🇪", "hong kong": "🇭🇰"
}

COUNTRY_ISO = {
    "bangladesh": "BD", "india": "IN", "pakistan": "PK", "cameroon": "CM",
    "vietnam": "VN", "indonesia": "ID", "united states": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB", "russia": "RU", "brazil": "BR",
    "nigeria": "NG", "philippines": "PH", "egypt": "EG", "turkey": "TR",
    "thailand": "TH", "myanmar": "MM", "south africa": "ZA", "colombia": "CO",
    "kenya": "KE", "argentina": "AR", "algeria": "DZ", "sudan": "SD",
    "uae": "AE", "canada": "CA", "australia": "AU", "germany": "DE",
    "france": "FR", "italy": "IT", "spain": "ES", "japan": "JP",
    "china": "CN", "mexico": "MX", "saudi arabia": "SA", "malaysia": "MY",
    "singapore": "SG", "netherlands": "NL", "sweden": "SE", "norway": "NO",
    "denmark": "DK", "finland": "FI", "ireland": "IE", "belgium": "BE",
    "switzerland": "CH", "austria": "AT", "poland": "PL", "ukraine": "UA",
    "romania": "RO", "czech republic": "CZ", "hungary": "HU", "portugal": "PT",
    "greece": "GR", "israel": "IL", "south korea": "KR", "taiwan": "TW",
    "hong kong": "HK", "new zealand": "NZ", "chile": "CL", "peru": "PE",
    "morocco": "MA", "tunisia": "TN", "ghana": "GH", "ethiopia": "ET",
    "tanzania": "TZ", "uganda": "UG", "rwanda": "RW", "mozambique": "MZ",
    "senegal": "SN", "mali": "ML", "niger": "NE", "burkina faso": "BF",
    "benin": "BJ", "togo": "TG", "liberia": "LR", "sierra leone": "SL",
    "guinea": "GN", "gambia": "GM", "mauritania": "MR", "zambia": "ZM",
    "zimbabwe": "ZW", "malawi": "MW", "botswana": "BW", "namibia": "NA",
    "lesotho": "LS", "mauritius": "MU", "seychelles": "SC", "comoros": "KM",
    "madagascar": "MG", "somalia": "SO", "djibouti": "DJ", "eritrea": "ER",
    "burundi": "BI", "chad": "TD", "congo": "CG", "gabon": "GA",
    "equatorial guinea": "GQ", "libya": "LY", "yemen": "YE", "oman": "OM",
    "qatar": "QA", "bahrain": "BH", "kuwait": "KW", "jordan": "JO",
    "lebanon": "LB", "iraq": "IQ", "syria": "SY", "iran": "IR",
    "afghanistan": "AF", "turkmenistan": "TM", "uzbekistan": "UZ", "kazakhstan": "KZ",
    "kyrgyzstan": "KG", "tajikistan": "TJ", "azerbaijan": "AZ", "georgia": "GE",
    "armenia": "AM", "mongolia": "MN", "nepal": "NP", "bhutan": "BT",
    "sri lanka": "LK", "maldives": "MV", "brunei": "BN", "cambodia": "KH",
    "laos": "LA", "myanmar": "MM", "fiji": "FJ", "venezuela": "VE",
    "panama": "PA", "costa rica": "CR", "nicaragua": "NI", "honduras": "HN",
    "el salvador": "SV", "guatemala": "GT", "belize": "BZ", "cuba": "CU",
    "jamaica": "JM", "haiti": "HT", "dominican republic": "DO", "bahamas": "BS",
    "barbados": "BB", "iceland": "IS", "luxembourg": "LU", "slovenia": "SI",
    "croatia": "HR", "bosnia": "BA", "montenegro": "ME", "albania": "AL",
    "moldova": "MD", "belarus": "BY", "lithuania": "LT", "latvia": "LV",
    "estonia": "EE", "slovakia": "SK", "bulgaria": "BG", "serbia": "RS",
    "paraguay": "PY", "uruguay": "UY", "ecuador": "EC", "bolivia": "BO"
}

SERVICE_SHORTS = {
    "facebook": "FB", "whatsapp": "WA", "whatsapp businesses": "WB",
    "telegram": "TG", "instagram": "IG", "twitter": "TW", "x": "X",
    "google": "GO", "gmail": "GM", "youtube": "YT", "apple": "AP",
    "microsoft": "MS", "tiktok": "TT", "snapchat": "SC", "binance": "BN",
    "melbet": "MB", "bkash": "BK", "rocket": "RK", "nagad": "NG",
    "imo": "IMO", "messenger": "MS", "custom search": "CS"
}

# --- Premium Emoji Collection ---
EMOJI_COLLECTION = {
    # Social & Services
    "facebook": "📘", "whatsapp": "💚", "telegram": "✈️", "instagram": "📷",
    "twitter": "𝕏", "google": "🔍", "gmail": "📧", "youtube": "🎬",
    "apple": "🍎", "microsoft": "💻", "tiktok": "🎵", "snapchat": "👻",
    "binance": "💰", "melbet": "🎰", "bkash": "💳", "rocket": "🚀",
    "nagad": "📲", "imo": "💭", "messenger": "💬",
    
    # Status & Actions
    "done": "✅", "cross": "❌", "warning": "⚠️", "time": "⏰",
    "waiting": "🔄", "message": "📩", "otp": "🔐", "number": "📞",
    "world": "🌐", "user": "👤", "bot": "🤖", "live": "🟢",
    "off": "🔴", "traffic": "📊", "chart": "📈", "star": "⭐",
    "crown": "👑", "diamond": "💎", "fire": "🔥", "sparkles": "✨",
    "globe": "🌍", "pin": "📌", "note": "📝", "gear": "⚙️",
    "link": "🔗", "plus": "➕", "trash": "🗑️", "gift": "🎁",
    "shield": "🛡️", "key": "🔑", "lock": "🔒", "bell": "🔔",
    "rocket_launch": "🚀", "trophy": "🏆", "medal": "🎖️", "target": "🎯",
    "lightning": "⚡", "bulb": "💡", "tools": "🛠️", "package": "📦",
    "mega": "📢", "hi": "👋", "refresh": "🔄", "chart_up": "📈",
    "premium": "💫", "vip": "🌟", "elite": "💠", "pro": "🎯"
}

def get_country_flag(country_name):
    if not country_name:
        return "🌍"
    name = str(country_name).lower().strip()
    if name in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[name]
    for country, flag in COUNTRY_FLAGS.items():
        if len(country) >= 4 and (country in name or name in country):
            return flag
    return "🌍"

def get_iso_code(country_name):
    name = str(country_name).lower().strip()
    if name in COUNTRY_ISO:
        return COUNTRY_ISO[name]
    for country, iso in COUNTRY_ISO.items():
        if country in name or name in country:
            return iso
    return name[:2].upper() if len(name) >= 2 else "UN"

def emo(keyword, default="✨"):
    if not keyword:
        return default
    kw = str(keyword).lower().strip()
    if kw in EMOJI_COLLECTION:
        return EMOJI_COLLECTION[kw]
    for key, emoji in EMOJI_COLLECTION.items():
        if len(key) >= 3 and key in kw:
            return emoji
    flag = get_country_flag(kw)
    if flag != "🌍":
        return flag
    return default

def get_short_service(service_name):
    name = str(service_name).lower().strip()
    return SERVICE_SHORTS.get(name, name[:2].upper() if len(name) >= 2 else "SV")

def format_url(url):
    url = url.strip()
    if url and not url.startswith(('http://', 'https://', 'tg://')): 
        return 'https://' + url
    return url

def extract_channel_username(url):
    if "t.me/" in url:
        parts = url.split("t.me/")
        if len(parts) > 1:
            username = parts[1].split("/")[0].split("?")[0]
            if not username.startswith("@"): 
                username = "@" + username
            return username
    return ""

def mask_number(phone):
    phone_str = str(phone).replace('+', '')
    if len(phone_str) > 7: 
        return f"{phone_str[:3]}VIP{phone_str[-4:]}"
    return phone_str

def safe_send(chat_id, text, reply_markup=None, message_id=None):
    try:
        clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
        if message_id:
            return bot.edit_message_text(clean_text, chat_id=chat_id, message_id=message_id, parse_mode="HTML", reply_markup=reply_markup)
        else:
            return bot.send_message(chat_id, clean_text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        error_msg = str(e).lower()
        if "not modified" in error_msg: 
            return None
        return None

def load_data():
    with data_lock:
        if not os.path.exists(DATA_FILE):
            default_data = {
                "users": [], "services_data": {}, "forward_groups": [], 
                "main_otp_link": "https://t.me/", "watermark": "VIP NUMBER CLUB",
                "force_join_enabled": False, "force_join_channels": []
            }
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        try:
            with open(DATA_FILE, "r", encoding='utf-8') as f:
                content = f.read().strip()
                if not content: 
                    return {"users": [], "services_data": {}, "forward_groups": [], "main_otp_link": "https://t.me/", "watermark": "VIP NUMBER CLUB", "force_join_enabled": False, "force_join_channels": []}
                data = json.loads(content)
                if "force_join_enabled" not in data: data["force_join_enabled"] = False
                if "force_join_channels" not in data: data["force_join_channels"] = []
                if "flags" in data: del data["flags"]
                for grp in data.get("forward_groups", []):
                    if "buttons" not in grp:
                        grp["buttons"] = []
                        if grp.get("btn_name") and grp.get("btn_url"):
                            grp["buttons"].append({"name": grp["btn_name"], "url": grp["btn_url"]})
                return data
        except:
            return {"users": [], "services_data": {}, "forward_groups": [], "main_otp_link": "https://t.me/", "watermark": "VIP NUMBER CLUB", "force_join_enabled": False, "force_join_channels": []}

def save_data(data):
    with data_lock:
        try:
            if "flags" in data: del data["flags"]
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except: pass

def add_user(user_id):
    data = load_data()
    if user_id not in data.get("users", []):
        data.setdefault("users", []).append(user_id)
        save_data(data)

def get_total_ranges():
    data = load_data()
    count = 0
    for srv in data.get("services_data", {}).values():
        for cnt in srv.get("countries", {}).values():
            count += len(cnt.get("ranges", {}))
    return count

def check_force_join(user_id):
    if user_id == ADMIN_ID: return True 
    data = load_data()
    if not data.get("force_join_enabled"): return True
    channels = data.get("force_join_channels", [])
    if not channels: return True 
    for link in channels:
        chat_username = extract_channel_username(link)
        if not chat_username: continue 
        try:
            member = bot.get_chat_member(chat_username, user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False 
        except: pass
    return True 

def show_force_join_message(chat_id, message_id=None):
    data = load_data()
    channels = data.get("force_join_channels", [])
    text = (
        f"{emo('warning')} <b>ACCESS DENIED</b> {emo('warning')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 Join our channels to use this bot\n\n"
        f"Click <b>JOINED</b> after joining"
    )
    markup = InlineKeyboardMarkup()
    for link in channels:
        markup.add(InlineKeyboardButton(text="📢 Join Channel", url=link))
    markup.add(InlineKeyboardButton(text="✅ JOINED ✅", callback_data="check_join"))
    safe_send(chat_id, text, markup, message_id)

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(f"📱 GET NUMBER"), KeyboardButton(f"📊 TRAFFIC"))
    if user_id == ADMIN_ID: markup.add(KeyboardButton(f"⚙️ ADMIN PANEL"))
    return markup

def get_admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛠️ Manage Services", callback_data="admin_manage_service"),
        InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"),
        InlineKeyboardButton("🔗 Group Settings", callback_data="admin_group_settings"),
        InlineKeyboardButton("📣 Force Join Settings", callback_data="admin_force_join"),
        InlineKeyboardButton("💎 Set Watermark", callback_data="admin_set_watermark")
    )
    return markup

def get_force_join_menu():
    data = load_data()
    is_enabled = data.get("force_join_enabled", False)
    channels = data.get("force_join_channels", [])
    status_text = "🟢 ENABLED" if is_enabled else "🔴 DISABLED"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(f"Toggle: {status_text}", callback_data="toggle_force_join"))
    for idx, link in enumerate(channels):
        markup.add(InlineKeyboardButton(f"❌ Remove: {link}", callback_data=f"delfjc_{idx}"))
    markup.add(InlineKeyboardButton("➕ Add Channel", callback_data="add_fjc"))
    markup.add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    return markup

def get_group_settings_menu():
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=1)
    otp_link = data.get("main_otp_link", "")
    markup.add(InlineKeyboardButton("🔗 Set OTP Group Link", callback_data="set_main_otp_link"))
    if otp_link and otp_link != "https://t.me/":
        markup.add(InlineKeyboardButton("🗑️ Remove OTP Link", callback_data="del_main_otp_link"))
    markup.add(InlineKeyboardButton("➕ Add Forward Group", callback_data="add_fwd_group"))
    fwd_groups = data.get("forward_groups", [])
    if fwd_groups:
        markup.add(InlineKeyboardButton("📋 ADDED GROUPS 📋", callback_data="ignore"))
        for grp in fwd_groups:
            btn_count = len(grp.get('buttons', []))
            markup.add(InlineKeyboardButton(f"⚙️ {grp['chat_id']} [{btn_count} Btns]", callback_data=f"editgrp_{grp['chat_id']}"))
    markup.add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    return markup

def show_edit_group_menu(chat_id, grp_id, message_id=None):
    data = load_data()
    grp = next((g for g in data.get("forward_groups", []) if str(g["chat_id"]) == str(grp_id)), None)
    if not grp:
        safe_send(chat_id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), message_id)
        return
    text = (
        f"⚙️ <b>MANAGE GROUP</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📱 ID: <code>{grp_id}</code>\n"
        f"🔘 Buttons: {len(grp.get('buttons', []))}"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, btn in enumerate(grp.get("buttons", [])):
        markup.add(InlineKeyboardButton(f"❌ {btn['name']}", callback_data=f"delgrpbtn_{grp_id}_{idx}"))
    markup.add(InlineKeyboardButton("➕ Add Button", callback_data=f"addgrpbtn_{grp_id}"))
    markup.add(InlineKeyboardButton("🗑️ Delete Group", callback_data=f"delfwd_{grp_id}"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_group_settings"))
    safe_send(chat_id, text, markup, message_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)
    if not check_force_join(user_id):
        show_force_join_message(message.chat.id)
        return
    show_main_menu(message.chat.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)

    if "GET NUMBER" in text:
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_user_services(message.chat.id)
    elif "TRAFFIC" in text:
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_traffic_search(message.chat.id)
    elif "ADMIN PANEL" in text:
        if user_id == ADMIN_ID:
            show_admin_panel(message.chat.id)
        else:
            bot.send_message(message.chat.id, f"{emo('warning')} <b>Access Denied!</b>", parse_mode="HTML")

def show_main_menu(chat_id, first_name=None, message_id=None):
    if not first_name:
        try: first_name = bot.get_chat(chat_id).first_name
        except: first_name = "VIP User"
    data = load_data()
    watermark = data.get("watermark", "VIP NUMBER CLUB")
    text = (
        f"{emo('crown')} <b>VIP NUMBER CLUB</b> {emo('crown')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('hi')} Welcome, <a href='tg://user?id={chat_id}'>{html.escape(first_name)}</a>!\n\n"
        f"{emo('star')} Premium OTP Service {emo('star')}\n\n"
        f"📱 Tap GET NUMBER to start\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('fire')} {html.escape(watermark)} {emo('fire')}"
    )
    safe_send(chat_id, text, get_main_menu(chat_id), message_id)

def show_user_services(chat_id, message_id=None):
    data = load_data()
    m
