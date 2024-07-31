from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytonconnect import TonConnect
from .cfg import *
from .user import User
from .get_course_bull import readcource as course
from .timer import get_current_time, check_time_difference
import aiohttp
import logging

logging.basicConfig(level=logging.DEBUG)


wallet_list = TonConnect.get_wallets()

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


def get_collections():
    return [
        [
            "https://getgems.io/collection/EQBkznf-y_ne6eBNdPUKNxr44kPw7Cff6oxT2rWcuv76BSk3",
            "Booli TON",
            "100",
            "EQBkznf-y_ne6eBNdPUKNxr44kPw7Cff6oxT2rWcuv76BSk3",
        ],
        [
            "https://getgems.io/collection/EQDhqB3Fw76kl3vtqABg5gkEtHlAxGlB-mYJWmMOkkVnz3TC",
            "Bull Pass",
            "50",
            "EQDhqB3Fw76kl3vtqABg5gkEtHlAxGlB-mYJWmMOkkVnz3TC",
        ],
    ]


async def check_collection_ownership(address, collection):
    url = f"https://tonapi.io/v2/accounts/{address}/nfts?collection={collection}&limit=1000&offset=0&indirect_ownership=false"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.error(f"Failed to fetch data: {response.status}")
                    return False
                data = await response.json()
                nft_items = data.get("nft_items", [])
    except aiohttp.ClientError as e:
        logging.error(f"Client error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False

    return bool(nft_items)


async def check_nft_in_address_for_text(address):
    collections = get_collections()

    text = ""
    for collection in collections:
        if not await check_collection_ownership(address, collection[3]):
            text += f"\n\n❌ NFT из коллекции <a href='{collection[0]}'>{collection[1]}</a> отсутствует\n🔋 Даёт +{collection[2]}% к награде"
        else:
            text += f"\n\n✅ NFT из коллекции <a href='{collection[0]}'>{collection[1]}</a>\n🔋 Даёт +{collection[2]}% к награде"

    return text


async def check_nft_in_address_for_mining(address, mining_result):
    collections = get_collections()

    result = mining_result
    for collection in collections:
        if await check_collection_ownership(address, collection[3]):
            result += (mining_result / 100) * int(collection[2])

    return result


@app.callback_query(F.data == "mining")
async def mining_callback(query: CallbackQuery):
    user_id = query.from_user.id
    sub = await check_sub(user_id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await query.answer(text=text, show_alert=True)
    else:
        user = User(user_id)
        user.add_user(None)

        user.set_name(query.from_user.username)
        user_info = user.get_info()
        address = user.get_address()

        if not address:
            text_fragment = "\n\n⚠ Подключите кошелёк чтобы получать дополнительные награды за майнинг"
        else:
            text_fragment = await check_nft_in_address_for_text(address)

        text = f"💎 Майнинг\n\n💰 Награда за майнинг: {await check_nft_in_address_for_mining(address, user_info['mining']['result'])} $BULL\n🕑 Время работы: {user_info['mining']['hours']} часов{text_fragment}"
        markup = [
            [
                InlineKeyboardButton(
                    text=(
                        "⚡ Запустить майнинг"
                        if user_info["mining"]["state"] == ""
                        else "⚡ Получить награду"
                    ),
                    callback_data=(
                        "start_mining"
                        if user_info["mining"]["state"] == ""
                        else "get_mined_bull"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
            ],
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard,
        )


@app.callback_query(F.data == "start_mining")
async def start_mining_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)
    user.add_user(None)

    user.set_name(query.from_user.username)

    user_info = user.get_info()

    text = f"✅ Майнинг успешно запущен!\n🕑 Получить награду можно через {user_info['mining']['hours']} часов!"
    markup = [
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back")],
    ]

    user.set_mining_state(f"'{get_current_time()}'")

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=keyboard,
    )


@app.callback_query(F.data.startswith("get_mined_bull"))
async def get_mined_bull_callback(query: CallbackQuery):
    user_id = query.from_user.id
    sub = await check_sub(user_id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await query.answer(text=text, show_alert=True)
    else:
        
        user = User(user_id)
        user.add_user(None)

        user.set_name(query.from_user.username)
        user_info = user.get_info()
        amount = user_info["mining"]["result"]
        amount = await check_nft_in_address_for_mining(user.get_address(), amount)
        state = user.get_mining_state()
        usd = "(<i>" + str(round(amount * course(), 3)) + "$</i>) "
        text = f"✅ Вы успешно получили награду, на ваш счет начислено - {amount} $BULL {usd}."
        markup = [
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="mining"),
            ]
        ]

        mining_timer = check_time_difference(state, user_info["mining"]["hours"])

        if mining_timer != True:
            text = f"⚠ Ожидайте, до окончания майнинга осталось - {mining_timer}"
            await query.answer(text=text, show_alert=True)
        else:
            refferer = user.update_refferer()

            if refferer:
                await bot.send_message(
                    text=f"👤 @{query.from_user.username} получил первую награду за майнинг и стал вашим рефералом!",
                    chat_id=refferer,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="✅ Закрыть", callback_data="close"
                                )
                            ]
                        ]
                    ),
                )

            balance = user.get_balance()
            balance["bull"] = balance["bull"] + float(amount)
            user.set_balance(balance)
            user.set_mining_state("''")

            keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

            await bot.edit_message_text(
                chat_id=user_id,
                message_id=query.message.message_id,
                text=text,
                reply_markup=keyboard,
            )
