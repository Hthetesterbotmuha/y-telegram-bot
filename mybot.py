import asyncio
import json
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "7854334560:AAF45884N8FkM5amESBMvvATp9pJczi450Y"
ADMIN_ID = 7506897346  # ID-и админи ботро ворид кунед

bot = Bot(token=TOKEN)
dp = Dispatcher()

Мағозаи файлҳо барои нигоҳдорӣ

file_store = {}
download_limit = {}  # Мағозаи маҳдудияти зеркашӣ (ID-и файл → шумора)

Захира кардани файлҳо дар файли "files.json"

def save_files():
with open("files.json", "w") as f:
json.dump({"files": file_store, "limits": download_limit}, f)

Барқарор кардани файлҳо ҳангоми оғоз

def load_files():
global file_store, download_limit
try:
with open("files.json", "r") as f:
data = json.load(f)
file_store = data.get("files", {})
download_limit = data.get("limits", {})
except FileNotFoundError:
file_store = {}
download_limit = {}

load_files()

Ҳолатҳои корбаронро нигоҳ медорад (масалан, интизории маҳдудияти зеркашӣ)

user_states = {}

async def check_subscription(user_id):
current_time = time.time()

# Пок кардани каналҳое, ки мӯҳлаташон ба охир расидааст  
for channel, expiration in list(CHANNELS.items()):  
    if current_time > expiration:  
        del CHANNELS[channel]  
        del channel_expiration[channel]  

# Санҷиш кардани обунаи корбар  
for channel in CHANNELS:  
    try:  
        member = await bot.get_chat_member(channel, user_id)  
        if member.status not in ["member", "administrator", "creator"]:  
            return False  # Агар корбар обуна нашуда бошад  
    except:  
        # Агар канал ёфт нашавад ё хатогӣ пайдо шавад  
        continue  

return True  # Агар корбар ба ҳамаи каналҳо обуна бошад

Захираи реклама ва мӯҳлати фиристодан

advertisement_text = "📢 Ба канали мо обуна шавед ва файлҳои бештар гиред! 🔥 Клик кунед"
advertisement_photo = None  # Акс барои реклама
advertisement_end_time = 0  # Вақти анҷоми реклама
advertisement_active = False  # Оё реклама фаъол аст?

Каналҳои обунашавӣ ва мӯҳлати онҳо

CHANNELS = {}  # канал -> мӯҳлати анҷом
channel_expiration = {}  # канал -> мӯҳлати анҷом

Тугмаи обунашавӣ

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
subscribe_keyboard = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="✅ Ман обуна шудам", callback_data="check_subscription")]
])

Тугмаҳо барои админ

admin_keyboard = ReplyKeyboardMarkup(
keyboard=[
[KeyboardButton(text="📊 Статистика")],
[KeyboardButton(text="📢 Реклама")],
[KeyboardButton(text="📺 Каналҳо")]
],
resize_keyboard=True
)

@dp.message(Command("start"))
async def welcome(message: Message):
global advertisement_active

# Check if there's a file ID argument  
args = message.text.split()  
if len(args) > 1:  
    file_id = args[1]  
    if file_id in file_store:  
        # 📌 Санҷиши обунаи корбар  
        if CHANNELS and not await check_subscription(message.from_user.id):  
            channels_list = "\n".join([f"📺 {channel}" for channel in CHANNELS.keys()])  
            await message.answer(  
                f"❗ Барои гирифтани файл, шумо бояд ба каналҳои шарикон обуна шавед ⬇️\n\n{channels_list}\n\n"  
                "✅ Пас аз обуна шудан, тугмаи 'Ман обуна шудам'-ро пахш кунед!",   
                reply_markup=subscribe_keyboard  
            )  
            return  
          
        if download_limit.get(file_id, 1) > 0:  
            # Send the requested file  
            try:  
                await message.answer_document(file_store[file_id])  
                download_limit[file_id] -= 1  
                save_files()  
                  
                # 📌 Бот рекламаро **танҳо дар мӯҳлати муқарраршуда** мефиристад  
                if advertisement_active and time.time() < advertisement_end_time:  
                    if advertisement_photo:  
                        await message.answer_photo(advertisement_photo, caption=advertisement_text, parse_mode="Markdown")  
                    else:  
                        await message.answer(advertisement_text, parse_mode="Markdown")  
                else:  
                    advertisement_active = False  # Бот рекламаро дигар намефиристад  
                return  
            except:  
                await message.answer("❌ Файл ёфт нашуд!")  
                return  
        else:  
            await message.answer("🚫 Мӯҳлати зеркашии ин файл ба охир расид!")  
            return  

# Send welcome message with admin keyboard if admin  
if message.from_user.id == ADMIN_ID:  
    await message.answer("👋🏻 Хуш омадед, админ!", reply_markup=admin_keyboard)  
else:  
    await message.answer(  
        "👋🏻 **Хуш омадед!**\n\n"  
        "💾 **Бо ёрии ин бот, шумо метавонед файлҳои гуногунро бо осонӣ дарёфт кунед.**\n\n"  
        "⚡ **Интихоб кунед тугмаро, ки ба шумо лозим аст ва оғоз кунед!**",  
        parse_mode="Markdown"  
    )

@dp.message(lambda message: message.content_type in ["document", "photo", "video", "audio"])
async def save_file(message: Message):
if message.from_user.id == ADMIN_ID:
file_id = None
if message.document:
file_id = message.document.file_id
elif message.photo:
file_id = message.photo[-1].file_id
elif message.video:
file_id = message.video.file_id
elif message.audio:
file_id = message.audio.file_id

if file_id:  
        # Нигоҳ доштани file_id дар ҳолати корбар  
        user_states[message.from_user.id] = {"file_id": file_id, "waiting_for_limit": True}  
        await message.answer("🔢 Лутфан шумораи иҷозатдодаи зеркаширо ворид кунед (20, 40, 50, 100...)")  
    else:  
        await message.answer("❌ Файл нодуруст аст.")  
else:  
    await message.answer("🚫 Танҳо админ метавонад файл ирсол кунад!")

@dp.message(lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_limit"))
async def set_download_limit(message: Message):
if not message.text.isdigit():
await message.answer("❌ Лутфан рақами дурустро ворид кунед!")
return

user_id = message.from_user.id  
if user_id in user_states and user_states[user_id]["waiting_for_limit"]:  
    file_id = user_states[user_id]["file_id"]  
    unique_id = str(len(file_store) + 1)  
    file_store[unique_id] = file_id  
    download_limit[unique_id] = int(message.text)  
    save_files()  
      
    # 📌 Бот **пас аз ворид кардани шумораи зеркашӣ** ссылка медиҳад!  
    bot_info = await bot.get_me()  
    link = f"https://t.me/{bot_info.username}?start={unique_id}"  
    await message.answer(f"✅ Файл сабт шуд! Ссылкаи зеркашӣ: {link}")  
      
    # Clear user state  
    user_states.pop(user_id)  
else:  
    await message.answer("❌ Хатогӣ. Лутфан, файлро дубора бор кунед.")

@dp.message(lambda message: message.text == "📊 Статистика")
async def show_stats(message: Message):
if message.from_user.id == ADMIN_ID:
await message.answer(f"📊 Статистикаи бот:\n\n"
f"👥 Корбарон: {len(file_store)}\n"
f"📂 Файлҳои боргузоришуда: {len(file_store)}",
parse_mode="Markdown")
else:
await message.answer("🚫 Ин функсия танҳо барои админ аст!")

@dp.message(lambda message: message.text == "📢 Реклама")
async def set_advertisement(message: Message):
if message.from_user.id == ADMIN_ID:
user_states[message.from_user.id] = {"waiting_for_ad_text": True}
await message.answer("✍️ Лутфан матни нави рекламаро ворид кунед:")
else:
await message.answer("🚫 Ин функсия танҳо барои админ аст!")

@dp.message(lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_ad_text"))
async def save_advertisement(message: Message):
global advertisement_text
user_id = message.from_user.id
advertisement_text = message.text
user_states[user_id] = {"waiting_for_ad_photo": True}
await message.answer("📸 Ҳоло акс барои реклама фиристед (ё 'skip' нависед агар акс намехоҳед):")

@dp.message(lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_ad_photo"))
async def save_advertisement_photo(message: Message):
global advertisement_photo
user_id = message.from_user.id

if message.photo:  
    advertisement_photo = message.photo[-1].file_id  
    user_states[user_id] = {"waiting_for_ad_duration": True}  
    await message.answer("✅ Акс захира шуд! ⏳ Ҳоло вақти интизориро (дақиқа) ворид кунед: 10, 20, 30, 60...")  
elif message.text and message.text.lower() == "skip":  
    advertisement_photo = None  
    user_states[user_id] = {"waiting_for_ad_duration": True}  
    await message.answer("⏳ Лутфан вақти интизориро (дақиқа) ворид кунед: 10, 20, 30, 60...")  
else:  
    await message.answer("❌ Лутфан акс фиристед ё 'skip' нависед!")

@dp.message(lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_ad_duration"))
async def set_advertisement_duration(message: Message):
global advertisement_end_time, advertisement_active
user_id = message.from_user.id

if not message.text.isdigit():  
    await message.answer("❌ Лутфан рақами дурустро ворид кунед!")  
    return  
  
duration_minutes = int(message.text)  
advertisement_end_time = time.time() + (duration_minutes * 60)  # Ҳисоб кардани вақти анҷом  
advertisement_active = True  # Фаъол кардани реклама  
await message.answer(f"✅ Реклама барои {message.text} дақиқа фаъол хоҳад буд!")  
  
# Clear user state  
user_states.pop(user_id, None)

@dp.callback_query(lambda callback: callback.data == "check_subscription")
async def verify_subscription(callback):
if await check_subscription(callback.from_user.id):
await callback.message.edit_text("✅ Обунаи шумо тасдиқ шуд! Ҳоло метавонед файлҳоро зеркашӣ кунед.")
else:
await callback.message.edit_text("❌ Шумо ҳанӯз обуна нашудаед. Лутфан аввал обуна шавед ва пас тугмаи '✅ Ман обуна шудам'-ро пахш кунед.")
await callback.answer()

Тугмаҳо барои идоракунии каналҳо

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_channel_management_keyboard():
return InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="➕ Илова кардани канал", callback_data="add_channel")],
[InlineKeyboardButton(text="🗑 Ҳазф кардани канал", callback_data="remove_channel")],
[InlineKeyboardButton(text="📋 Рӯйхати каналҳо", callback_data="list_channels")]
])

@dp.message(lambda message: message.text == "📺 Каналҳо")
async def manage_channels(message: Message):
if message.from_user.id == ADMIN_ID:
await message.answer(
"📺 Идоракунии каналҳо\n\n"
"Интихоб кунед амале, ки мехоҳед иҷро кунед:",
reply_markup=get_channel_management_keyboard(),
parse_mode="Markdown"
)
else:
await message.answer("🚫 Ин функсия танҳо барои админ аст!")

@dp.callback_query(lambda callback: callback.data == "add_channel")
async def add_channel_callback(callback):
if callback.from_user.id == ADMIN_ID:
user_states[callback.from_user.id] = {"waiting_for_channel": True}
await callback.message.edit_text(
"🔗 Илова кардани канали нав\n\n"
"Лутфан username-и каналро бо @ ворид кунед (масалан: @example_channel):"
)
await callback.answer()

@dp.callback_query(lambda callback: callback.data == "remove_channel")
async def remove_channel_callback(callback):
if callback.from_user.id == ADMIN_ID:
if CHANNELS:
channels_buttons = []
for channel in CHANNELS.keys():
channels_buttons.append([InlineKeyboardButton(
text=f"🗑 {channel}",
callback_data=f"delete_{channel}"
)])
channels_buttons.append([InlineKeyboardButton(text="🔙 Бозгашт", callback_data="back_to_channels")])

keyboard = InlineKeyboardMarkup(inline_keyboard=channels_buttons)  
        await callback.message.edit_text(  
            "🗑 **Ҳазф кардани канал**\n\n"  
            "Каналеро интихоб кунед, ки мехоҳед ҳазф кунед:",  
            reply_markup=keyboard  
        )  
    else:  
        await callback.message.edit_text(  
            "❌ **Ҳеҷ канале барои ҳазф мавҷуд нест!**",  
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[  
                [InlineKeyboardButton(text="🔙 Бозгашт", callback_data="back_to_channels")]  
            ])  
        )  
await callback.answer()

@dp.callback_query(lambda callback: callback.data == "list_channels")
async def list_channels_callback(callback):
if callback.from_user.id == ADMIN_ID:
if CHANNELS:
channels_list = "\n".join([
f"📺 {channel} (то {time.strftime('%Y-%m-%d %H:%M', time.localtime(exp))})"
for channel, exp in CHANNELS.items()
])
await callback.message.edit_text(
f"📋 Каналҳои фаъол:\n\n{channels_list}",
reply_markup=InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🔙 Бозгашт", callback_data="back_to_channels")]
])
)
else:
await callback.message.edit_text(
"📋 Рӯйхати каналҳо\n\n"
"Ҳанӯз канале илова нашудааст.",
reply_markup=InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🔙 Бозгашт", callback_data="back_to_channels")]
])
)
await callback.answer()

@dp.callback_query(lambda callback: callback.data.startswith("delete_"))
async def delete_channel_callback(callback):
if callback.from_user.id == ADMIN_ID:
channel_to_delete = callback.data.replace("delete_", "")
if channel_to_delete in CHANNELS:
del CHANNELS[channel_to_delete]
del channel_expiration[channel_to_delete]
await callback.message.edit_text(
f"✅ Канали {channel_to_delete} бо муваффақият ҳазф шуд!",
reply_markup=InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🔙 Бозгашт", callback_data="back_to_channels")]
])
)
else:
await callback.message.edit_text(
"❌ Канал ёфт нашуд!",
reply_markup=InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🔙 Бозгашт", callback_data="back_to_channels")]
])
)
await callback.answer()

@dp.callback_query(lambda callback: callback.data == "back_to_channels")
async def back_to_channels_callback(callback):
if callback.from_user.id == ADMIN_ID:
await callback.message.edit_text(
"📺 Идоракунии каналҳо\n\n"
"Интихоб кунед амале, ки мехоҳед иҷро кунед:",
reply_markup=get_channel_management_keyboard()
)
await callback.answer()

@dp.message(lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_channel"))
async def add_channel(message: Message):
user_id = message.from_user.id
channel_username = message.text.strip()

if not channel_username.startswith("@"):  
    await message.answer("❌ Лутфан username-и каналро бо @ оғоз кунед (масалан: @example_channel)")  
    return  
  
# Санҷиши канали мавҷудбуда  
if channel_username in CHANNELS:  
    await message.answer(f"⚠️ Канали {channel_username} аллакай мавҷуд аст!")  
    user_states.pop(user_id, None)  
    return  
  
user_states[user_id] = {"waiting_for_channel_duration": True, "channel": channel_username}  
await message.answer("⏳ Лутфан мӯҳлати фаъолияти каналро (соат) ворид кунед: 12, 24, 48, 72...")

@dp.message(lambda message: message.from_user.id in user_states and user_states[message.from_user.id].get("waiting_for_channel_duration"))
async def set_channel_duration(message: Message):
global CHANNELS, channel_expiration
user_id = message.from_user.id

if not message.text.isdigit():  
    await message.answer("❌ Лутфан рақами дурустро ворид кунед!")  
    return  
  
duration_hours = int(message.text)  
channel = user_states[user_id]["channel"]  
expiration_time = time.time() + (duration_hours * 3600)  # Ҳисоб кардани вақти анҷом дар соат  
  
# Санҷиши мавҷудбудани канал пеш аз илова кардан  
try:  
    # Озмоиши дастрасии канал  
    chat_info = await bot.get_chat(channel)  
      
    CHANNELS[channel] = expiration_time  
    channel_expiration[channel] = expiration_time  
      
    await message.answer(f"✅ Канали {channel} барои {duration_hours} соат илова шуд!")  
except Exception as e:  
    await message.answer(f"❌ Хатогӣ: Канали {channel} ёфт нашуд ё бот ба он дастрасӣ надорад!")  
  
# Clear user state  
user_states.pop(user_id, None)

async def main():
load_files() # Load files on startup
await dp.start_polling(bot)

if name == "main":
asyncio.run(main())

