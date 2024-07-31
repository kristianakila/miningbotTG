from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Filter
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from .user import User
from .cfg import *

app = Router()


async def check_sub(user_id):
    try:
        sub_list = ["member", "administrator", "creator"]
        channels = ["-1002004552099", "-1002140229897"]
        for i in channels:
            _ = await bot.get_chat_member(i, user_id)
            if _.status.name.lower() not in sub_list:
                return False
        return True
    except:
        return True


@app.message(Command("start"))
async def start_cmd(message: Message) -> None:
    chat_type = message.chat.type
    user_id = message.from_user.id

    text = (
        f"Приветствуем — @{message.from_user.username}\n\n"
        "📋 Выполняйте 3 элементарных действия и получайте $BULL\n\n"
        "✅ Активируйте майнинг\n"
        "✅ Выполняйте задания\n"
        "✅ Приглашайте друзей\n\n"
        "<a href='https://t.me/NFTBullTon'>🔗 Официальный канал</a>\n"
        "<a href='https://t.me/NFTBullChat'>🔗 Наш чат для общения</a>\n"
        "<a href='https://getgems.io/booli-ton'>🔗 NFT коллекция «Booli»</a>"
    )

    markup = [
        [
            InlineKeyboardButton(text="💎 Майнинг", callback_data="mining"),
            InlineKeyboardButton(text="💳 Кошелёк", callback_data="wallet"),
        ],
        [
            InlineKeyboardButton(text="👥 Реф. Система", callback_data="ref_system"),
            InlineKeyboardButton(text="📋 Задания", callback_data="tasks"),
        ],
        [InlineKeyboardButton(text="📊 Рейтинг", callback_data="top10")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    if chat_type == "private":
        sub = await check_sub(user_id)
        if not sub:
            text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
            keyboard = None
        user = User(user_id)

        ref = message.text.split(" ")
        if not len(ref) == 2:
            ref = None
        elif not ref[1].isdigit():
            ref = None
        else:
            ref = ref[1]

        user.add_user(ref)
        
        user.set_name(message.from_user.username)
        wstates = user.get_wstate()

        to_withdraw = "bull" if wstates["bull"] else ""

        if to_withdraw != "":
            await message.delete()

        await message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)


@app.callback_query(F.data == "back")
async def close_call(call: CallbackQuery) -> None:
    await call.answer()
    user_id = call.from_user.id

    text = (
        f"Приветствуем — @{call.from_user.username}\n\n"
        "📋 Выполняйте 3 элементарных действия и получайте $BULL\n\n"
        "✅ Активируйте майнинг\n"
        "✅ Выполняйте задания\n"
        "✅ Приглашайте друзей\n\n"
        "<a href='https://t.me/NFTBullTon'>🔗 Официальный канал</a>\n"
        "<a href='https://t.me/NFTBullChat'>🔗 Наш чат для общения</a>\n"
        "<a href='https://getgems.io/booli-ton'>🔗 NFT коллекция «Booli»</a>"
    )

    markup = [
        [
            InlineKeyboardButton(text="💎 Майнинг", callback_data="mining"),
            InlineKeyboardButton(text="💳 Кошелёк", callback_data="wallet"),
        ],
        [
            InlineKeyboardButton(text="👥 Реф. Система", callback_data="ref_system"),
            InlineKeyboardButton(text="📋 Задания", callback_data="tasks"),
        ],
        [InlineKeyboardButton(text="📊 Рейтинг", callback_data="top10")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@app.callback_query(F.data == "close")
async def close_call(call: CallbackQuery) -> None:
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    await call.answer()


@app.callback_query(F.data == "ref_system")
async def ref_call(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    sub = await check_sub(user_id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await call.answer(text=text, show_alert=True)
    else:
        await call.answer()
        user = User(user_id)
        user.add_user(None)

        user.set_name(call.from_user.username)
        bot_data = await bot.get_me()

        text = f"👥 Реферальная система\nПриглашайте друзей майнить $BULL вместе и получайте награды\n\n👤 Друзей: {user.get_ref_count()}\n💰 Награда: 50 $BULL\n\n🔗 Реф. Ссылка:\nhttps://t.me/{bot_data.username}?start={user_id}\n\n⚠️ Ваша награда будет зачислена после того, как реферал получит первую награду за майнинг."

        markup = [
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
            ],
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard,
        )


@app.callback_query(F.data == "top10")
async def top_call(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    top_users = User.get_top_10()

    if top_users:
        text = f"📊 Топ 10 майнеров $BULL\n"
        for user in top_users:
            text += f"\n👤 @{user['username']} - 💰 {user['bull']} $BULL"
    else:
        text = f"📊 Топ 10 майнеров $BULL"

    text += f"\n\n🐂 Всего {User.get_users_count()} майнеров."
    markup = [
        # [InlineKeyboardButton(text="👥 Топ 10 рефоводов", callback_data="top10ref")],
        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=keyboard,
    )
    await call.answer()


@app.callback_query(F.data == "top10ref")
async def topref_call(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    top_users = User.get_top_10_referrers()
    print(top_users)

    if top_users:
        text = f"👥 Топ 10 рефоводов\n\n"
        for name, count in top_users:
            text += f"👤 @{name} - 👥 {count} рефералов\n"
    else:
        text = f"👥 Топ 10 рефоводов\n\n"
    markup = [
        [InlineKeyboardButton(text="📊 Топ 10 майнеров $BULL", callback_data="top10")],
        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=keyboard,
    )
    await call.answer()
