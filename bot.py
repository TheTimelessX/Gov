# Handle seecalender query

from manager import UserManager
from conf import ( getToken, getAdmins )
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ( Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton )

import asyncio
import schedule
import threading
import time

calenders_step = {}
global manager
global managerx
manager = UserManager()
managerx = UserManager()
sch = schedule.Scheduler()
bot = AsyncTeleBot(
    getToken()
)

def handleScheduler():
    while 1:
        sch.run_pending()
        time.sleep(1)

def makeFont(string: str):
    return string.translate(
        string.maketrans("qwertyuiopasdfghjklzxcvbnm-1234567890", "Qᴡᴇʀᴛʏᴜɪᴏᴘᴀꜱᴅꜰɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ-𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎")
    )

@bot.message_handler()
async def onMessage(message: Message):
    if message.from_user.id in getAdmins():
        await manager.add(message.from_user.id, "leader")
        if message.text in (
            "panel",
            "/panel",
            "پنل"
        ):
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(makeFont("calender 📅"), callback_data=f"seecalenderpage_{message.from_user.id}_1")
            )
            markup.add(
                InlineKeyboardButton(makeFont("leaders 🦋"), callback_data=f"leaders_{message.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("polices 👮‍♂️"), callback_data=f"polices_{message.from_user.id}"),
                InlineKeyboardButton(makeFont("managers 👥"), callback_data=f"managers_{message.from_user.id}"),
            )
            markup.add(
                InlineKeyboardButton(makeFont("roles 🌊"), callback_data=f"roles_{message.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("close"), callback_data=f"close_{message.from_user.id}")
            )

            await bot.reply_to(message, makeFont("🔰 | Panel started from ") + f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>', parse_mode="HTML", reply_markup=markup)

    if message.text.startswith("پروفایل") or message.text.startswith("profile") or message.text.startswith("/profile"):
        if message.reply_to_message:
            profiles = await bot.get_user_profile_photos(message.reply_to_message.from_user.id)
            if profiles.total_count > 0:
                await bot.send_photo(
                    message.chat.id,
                    profiles.photos[0].file_id,
                    makeFont(f"📃 | name: ") + message.reply_to_message.from_user.full_name + makeFont(f"\n📪 | uid: {message.reply_to_message.from_user.id} | ") + message.reply_to_message.from_user.id + makeFont(f"💎 | role: {'local admin' if message.reply_to_message.from_user.id in getAdmins() else await manager.getRoleOfUser(message.reply_to_message.from_user.id)}\n👔 | username: {'null' if not message.reply_to_message.from_user.username else message.reply_to_message.from_user.username}"),
                    reply_to_message_id=message.id,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(makeFont("close"), callback_data=f'close_{message.from_user.id}')
                    )
                )
            else:
                profiles = await bot.get_user_profile_photos(message.from_user.id)
                await bot.reply_to(
                    message,
                    makeFont(f"📃 | name: ") + message.from_user.full_name + makeFont(f"\n📪 | uid: {message.from_user.id} | ") + message.from_user.id + makeFont(f"💎 | role: {'local admin' if message.from_user.id in getAdmins() else await manager.getRoleOfUser(message.from_user.id)}\n👔 | username: {'null' if not message.from_user.username else message.from_user.username}"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(makeFont("close"), callback_data=f'close_{message.from_user.id}')
                    )
                )

        else:
            if profiles.total_count > 0:
                await bot.send_photo(
                    message.chat.id,
                    profiles.photos[0].file_id,
                    makeFont(f"📃 | name: ") + message.from_user.full_name + makeFont(f"\n📪 | uid: {message.from_user.id} | ") + message.from_user.id + makeFont(f"💎 | role: {'local admin' if message.from_user.id in getAdmins() else await manager.getRoleOfUser(message.from_user.id)}\n👔 | username: {'null' if not message.from_user.username else message.from_user.username}"),
                    reply_to_message_id=message.id,
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(makeFont("close"), callback_data=f'close_{message.from_user.id}')
                    )
                )
            else:
                await bot.reply_to(
                    message,
                    makeFont(f"📃 | name: ") + message.reply_to_message.from_user.full_name + makeFont(f"\n📪 | uid: {message.reply_to_message.from_user.id} | ") + message.reply_to_message.from_user.id + makeFont(f"💎 | role: {'local admin' if message.reply_to_message.from_user.id in getAdmins() else await manager.getRoleOfUser(message.reply_to_message.from_user.id)}\n👔 | username: {'null' if not message.reply_to_message.from_user.username else message.reply_to_message.from_user.username}"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(makeFont("close"), callback_data=f'close_{message.from_user.id}')
                    )
                )

    elif message.text.startswith("برنامه"):
        if not message.from_user.id in calenders_step:
            calenders_step[message.from_user.id] = {}
            calenders_step[message.from_user.id]['uid'] = message.from_user.id
            calenders_step[message.from_user.id]['name'] = message.from_user.full_name
            calenders_step[message.from_user.id]['trigger'] = False
            calenders_step[message.from_user.id]['next'] = 300
            calenders_step[message.from_user.id]['message'] = ""
            calenders_step[message.from_user.id]['step'] = None

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(makeFont("trigger ❌"), callback_data=f"trigger_{message.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("timer ⏳"), callback_data=f"timer_{message.from_user.id}"),
                InlineKeyboardButton(makeFont("message 🔴"), callback_data=f"message_{message.from_user.id}")
            )

            markup.add(
                InlineKeyboardButton("✅", callback_data=f"addcalender_{message.from_user.id}")
            )

            rmsg = await bot.reply_to(
                message,
                makeFont(f"🏁 | making calender for [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n⏳ | timer: 5 mins"),
                reply_markup=markup,
                parse_mode="Markdown"
            )

            calenders_step[message.from_user.id]['message_id'] = rmsg.id

        else:
            ...

    if message.from_user.id in calenders_step:
        if calenders_step[message.from_user.id]['step'] == 'timer':
            if message.text.isdigit():
                calenders_step[message.from_user.id]['next'] = int(message.text)
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton(makeFont(f"trigger {'❌' if calenders_step[message.from_user.id]['trigger'] is False else '✅'}"), callback_data=f"trigger_{message.from_user.id}")
                )
                markup.add(
                    InlineKeyboardButton(makeFont("timer ⏳"), callback_data=f"timer_{message.from_user.id}"),
                    InlineKeyboardButton(makeFont(f"message {'🔴' if calenders_step[message.from_user.id]['message'].strip() != '' else '🔵'}"), callback_data=f"message_{message.from_user.id}")
                )

                markup.add(
                    InlineKeyboardButton("✅", callback_data=f"addcalender_{message.from_user.id}")
                )

                calenders_step[message.from_user.id]['step'] = None
                await bot.edit_message_text(
                    makeFont(f"🏁 | making calender for [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n⏳ | timer: {calenders_step[message.from_user.id]['next']} seconds"),
                    chat_id=message.chat.id,
                    message_id=message.id,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            else: await bot.reply_to(message, makeFont("🔓 | Inputed text is not a number"))

        elif calenders_step[message.from_user.id] == "message":
            calenders_step[message.from_user.id]['message'] = message.text
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(makeFont(f"trigger {'❌' if calenders_step[message.from_user.id]['trigger'] is False else '✅'}"), callback_data=f"trigger_{message.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("timer ⏳"), callback_data=f"timer_{message.from_user.id}"),
                InlineKeyboardButton(makeFont(f"message {'🔴' if calenders_step[message.from_user.id]['message'].strip() != '' else '🔵'}"), callback_data=f"message_{message.from_user.id}")
            )

            markup.add(
                InlineKeyboardButton("✅", callback_data=f"addcalender_{message.from_user.id}")
            )

            calenders_step[message.from_user.id]['step'] = None
            await bot.edit_message_text(
                makeFont(f"🏁 | making calender for [{message.from_user.full_name}](tg://user?id={message.from_user.id})\n⏳ | timer: {calenders_step[message.from_user.id]['next']} seconds"),
                chat_id=message.chat.id,
                message_id=message.id,
                reply_markup=markup,
                parse_mode="Markdown"
            )

@bot.callback_query_handler(lambda call: True)
async def onCallbackQueries(call: CallbackQuery):
    spl = call.data.split("_")
    uid = int(spl[1])
    if call.data.startswith("seecalenderpage"):
        if call.from_user.id == uid:
            try:
                page = int(spl[2])
                index_page = page-1
                hashes = await managerx.getCalenderHashes()
                h3 = managerx.s3to3(hashes)
                if len(h3) == 0:
                    await bot.edit_message_text(
                        makeFont("🔵 | No calender added"),
                        call.message.chat.id,
                        call.message.id,
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton(makeFont("back 🔙"), callback_data=f"back_{call.from_user.id}")
                        )
                    )

                elif len(h3) >= page:
                    cal_keys = InlineKeyboardMarkup()
                    opt = []
                    for key in h3[index_page]:
                        opt.append(
                            InlineKeyboardButton(makeFont(key), callback_data=f"seecalender_{call.from_user.id}_{key}")
                        )
                    
                    cal_keys.add(*opt)

                    if len(h3) > page and index_page != 0:
                        cal_keys.add(InlineKeyboardButton(makeFont("next ⏭"), callback_data=f"seecalenderpage_{call.from_user.id}_{page+1}"), InlineKeyboardButton(makeFont("previous ⏮"), callback_data=f"seecalenderpage_{call.from_user.id}_{page-1}"))
                        #cal_keys.add(InlineKeyboardButton(makeFont("previous ⏮"), callback_data=f"seecalenderpage_{call.from_user.id}_{page-1}"))

                    if len(h3) > page and not index_page != 0:
                        cal_keys.add(InlineKeyboardButton(makeFont("next ⏭"), callback_data=f"seecalenderpage_{call.from_user.id}_{page+1}"))
                    
                    if not len(h3) > page and index_page != 0:
                        cal_keys.add(InlineKeyboardButton(makeFont("previous ⏮"), callback_data=f"seecalenderpage_{call.from_user.id}_{page-1}"))
                    # if index_page != 0:
                    #     cal_keys.add(InlineKeyboardButton(makeFont("previous ⏮"), callback_data=f"seecalenderpage_{call.from_user.id}_{page-1}"))
                    
                    cal_keys.add(InlineKeyboardButton(makeFont("back 🔙"), callback_data=f"back_{call.from_user.id}"))

                    await bot.edit_message_text(
                        makeFont(f"💎 | Page {page}/{len(h3)}"),
                        call.message.chat.id,
                        call.message.id,
                        reply_markup=cal_keys
                    )

            except Exception as Errr:
                await bot.edit_message_text(
                    makeFont(f"🍷 | local error: {Errr}"),
                    call.message.chat.id,
                    call.message.id
                )

    elif call.data.startswith("back"):
        if call.from_user.id == uid:
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(makeFont("calender 📅"), callback_data=f"seecalenderpage_{call.from_user.id}_1")
            )
            markup.add(
                InlineKeyboardButton(makeFont("leaders 🦋"), callback_data=f"leaders_{call.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("polices 👮‍♂️"), callback_data=f"polices_{call.from_user.id}"),
                InlineKeyboardButton(makeFont("managers 👥"), callback_data=f"managers_{call.from_user.id}"),
            )
            markup.add(
                InlineKeyboardButton(makeFont("roles 🌊"), callback_data=f"roles_{call.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("close"), callback_data=f"close_{call.from_user.id}")
            )

            await bot.edit_message_text(
                makeFont("🔰 | Panel started from ") + f'<a href="tg://user?id={call.from_user.id}">{call.from_user.full_name}</a>', parse_mode="HTML", reply_markup=markup,
                chat_id=call.message.chat.id,
                message_id=call.message.id
            )

    elif call.data.startswith("leaders"):
        if call.from_user.id == uid:
            leaders = await managerx.getUsersByRole("leader")
            stx = f'🔐 | leaders are {len(leaders)}\n\n'
            for leader in leaders:
                stx += f"● | [{leader}](tg://user?id={leader})\n"

            await bot.edit_message_text(
                parse_mode="Markdown",
                text=stx,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(makeFont("back 🔙"), callback_data=f"back_{call.from_user.id}")
                )
            )

    elif call.data.startswith("polices"):
        if call.from_user.id == uid:
            polices = await managerx.getUsersByRole("police")
            stx = f'🔐 | polices are {len(polices)}\n\n'
            for police in polices:
                stx += f"● | [{police}](tg://user?id={police})\n"
                
            await bot.edit_message_text(
                parse_mode="Markdown",
                text=stx,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(makeFont("back 🔙"), callback_data=f"back_{call.from_user.id}")
                )
            )

    elif call.data.startswith("managers"):
        if call.from_user.id == uid:
            managers = await managerx.getUsersByRole("manager")
            stx = f'🔐 | managers are {len(managers)}\n\n'
            for manager in managers:
                stx += f"● | [{manager}](tg://user?id={manager})\n"
                
            await bot.edit_message_text(
                parse_mode="Markdown",
                text=stx,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(makeFont("back 🔙"), callback_data=f"back_{call.from_user.id}")
                )
            )

    elif call.data.startswith("roles"):
        if call.from_user.id == uid:
            await bot.edit_message_text(
                makeFont("🍃 | Leader\n🎲 | Manager\n👮‍♂️ | Police\n👤 | Member"),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(makeFont("back 🔙"), callback_data=f"back_{call.from_user.id}")
                )
            )

    elif call.data.startswith("close"):
        if call.from_user.id == uid:
            try:await bot.delete_message(call.message.chat.id, call.message.id)
            except:pass

    elif call.data.startswith("trigger"):
        if call.from_user.id == uid:
            calenders_step[call.from_user.id]['trigger'] = True if calenders_step[call.from_user.id]['trigger'] is False else False
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(makeFont(f"trigger {'❌' if calenders_step[call.from_user.id]['trigger'] is False else '✅'}"), callback_data=f"trigger_{call.from_user.id}")
            )
            markup.add(
                InlineKeyboardButton(makeFont("timer ⏳"), callback_data=f"timer_{call.from_user.id}"),
                InlineKeyboardButton(makeFont(f"message {'🔴' if calenders_step[call.from_user.id]['message'].strip() == '' else '🔵'}"), callback_data=f"message_{call.from_user.id}")
            )

            markup.add(
                InlineKeyboardButton("✅", callback_data=f"addcalender_{call.from_user.id}")
            )

            await bot.edit_message_text(
                makeFont(f"🏁 | making calender for [{call.from_user.full_name}](tg://user?id={call.from_user.id})\n⏳ | timer: {calenders_step[call.from_user.id]['next']} seconds"),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=markup,
                parse_mode="Markdown"
            )

    elif call.data.startswith("timer"):
        if call.from_user.id == uid:
            calenders_step[call.from_user.id]['step'] = "timer"
            await bot.reply_to(
                call.message,
                makeFont("🍷 | send your timer")
            )

    elif call.data.startswith("message"):
        if call.from_user.id == uid:
            calenders_step[call.from_user.id]['step'] = "message"
            await bot.reply_to(
                call.message,
                makeFont("🍷 | send your message")
            )

    elif call.data.startswith("addcalender"):
        if call.from_user.id == uid:
            await managerx.addToCalender(
                uid,
                call.from_user.full_name,
                calenders_step[call.from_user.id]['trigger'],
                calenders_step[call.from_user.id]['next'],
                calenders_step[call.from_user.id]['message']
            )
            await bot.edit_message_text(
                makeFont("🍬 | Your Calender signed !"),
                call.message.chat.id,
                calenders_step[call.from_user.id]['message_id']
            )
            del calenders_step[call.from_user.id]

if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
    thscheduler = threading.Thread(target=handleScheduler)
    thscheduler.start()
    thscheduler.join()