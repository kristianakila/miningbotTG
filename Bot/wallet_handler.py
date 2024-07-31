from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytonconnect import TonConnect
from .cfg import *
from .user import User
from .get_course_bull import readcource as course
from .connect_wallet import *
from .transfer import TransferJetton
from .transfer_message import send_transaction_tonconnect

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


@app.message(F.text)
async def withdraw_num_text(message: Message):
    user_id = message.from_user.id
    user = User(user_id)
    user.add_user(None)

    user.set_name(message.from_user.username)
    balance = user.get_balance()

    wstates = user.get_wstate()

    to_withdraw = "bull" if wstates["bull"] else ""

    if to_withdraw != "pppp":
        try:
            if to_withdraw == "bull":
                text = (
                    f"<blockquote>👛 Ваш баланс: {balance['bull']} $BULL (<i>{round(balance['bull'] * course(), 3)}$</i>)</blockquote> \n\n💸 Вывод {float(message.text)} $BULL (<i>{round(float(message.text) * course(), 3)}$</i>)"
                    if float(message.text) >= MIN_WITHDRAW_bull
                    else f"<blockquote>👛 Ваш баланс: {balance['bull']} $BULL (<i>{round(balance['bull'] * course(), 3)}$</i>)</blockquote> \n\n💵 Минимальная сумма вывода {MIN_WITHDRAW_bull} $BULL (<i>{round(MIN_WITHDRAW_bull * course(), 3)}$</i>)"
                )
                markup = (
                    [
                        [
                            InlineKeyboardButton(
                                text=f"❔ Вывести {float(message.text)} $BULL ({round(float(message.text) * course(), 3)}$)",
                                callback_data=f"verify_withdraw_bull_{float(message.text)}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="♻ Отменить", callback_data="back_withdraw"
                            )
                        ],
                    ]
                    if float(message.text) >= MIN_WITHDRAW_bull
                    else [
                        [
                            InlineKeyboardButton(
                                text="♻ Отменить", callback_data="back_withdraw"
                            )
                        ],
                    ]
                )
                if float(message.text) > balance["bull"]:
                    text = f"<blockquote>👛 Ваш баланс: {balance['bull']} $BULL (<i>{round(balance['bull'] * course(), 3)}$</i>)</blockquote> \n\n🤔 <b>Неверно введена сумма перевода!</b> \n\n<blockquote>Недостаточно денег на балансе для вывода {round(float(message.text), 3)} $BULL (<i>{round(float(message.text) * course(), 3)}$</i>)</blockquote>"
                    markup = [
                        [
                            InlineKeyboardButton(
                                text="♻ Отменить", callback_data="back_withdraw"
                            )
                        ],
                    ]
        except ValueError:
            text = f"<blockquote>👛 Ваш баланс: {balance['bull']} $BULL (<i>{round(balance['bull'] * course(), 3)}$</i>)</blockquote> \n\n🤔 <b>Неверно введена сумма перевода!</b> \n\n<blockquote>Это обязательно должно быть число <i>(например 10.25)</i></blockquote>"
            markup = [
                [
                    InlineKeyboardButton(
                        text="♻ Отменить", callback_data="back_withdraw"
                    )
                ],
            ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=int(wstates[to_withdraw]),
            text=text,
            reply_markup=keyboard,
        )
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)


@app.callback_query(F.data == "wallet")
async def wallet_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)
    conn = get_connector(user_id)
    conn_status = await conn.restore_connection()
    if not conn_status:
        if len(user.get_address()) == 48:
            user.set_address("''")

    sub = await check_sub(user_id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await query.answer(text=text, show_alert=True)
    else:
        await query.answer()
        user.add_user(None)

        user.set_name(query.from_user.username)
        address = user.get_address()
        balance = user.get_balance()

        text = f"💳 Кошелёк\n\n💵 Баланс: {balance['bull']} $BULL (<i>{round(balance['bull'] * course(), 3)}$</i>)\n\n👛 {await get_app_name(user_id)}:\n<code>{'Не привязан' if not address else address}</code>"
        markup = [
            # [
            #    InlineKeyboardButton(text="💸 Вывод", callback_data="withdraw"),
            # ],
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
                InlineKeyboardButton(
                    text=f"🔗 {'Привязать' if not address else 'Отвязать'}",
                    callback_data=f"{'connect' if not address else 'disconnect'}",
                ),
            ],
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard,
        )


@app.callback_query(F.data == "withdraw")
async def withdraw_callback(query: CallbackQuery):
    await query.answer()
    user_id = query.from_user.id

    text = f"💸 Выберите валюту для вывода:"

    markup = [
        [InlineKeyboardButton(text="🐂 $BULL", callback_data="withdraw_bull")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data=f"wallet")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=keyboard,
    )


@app.callback_query(F.data == "withdraw_bull")
async def withdraw_bull_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)

    user.set_name(query.from_user.username)
    balance = user.get_balance()
    text = f"<blockquote>👛 Ваш баланс: {balance['bull']} $BULL (<i>{round(balance['bull'] * course(), 3)}$</i>)</blockquote> \n\n💸 Введите сумму для перевода (Минимум {MIN_WITHDRAW_bull} $BULL (<i>{round(MIN_WITHDRAW_bull * course(), 3)}$</i>)):"
    markup = [
        [InlineKeyboardButton(text="♻ Отменить", callback_data="back_withdraw")],
    ]

    if balance["bull"] >= MIN_WITHDRAW_bull and user.get_address():
        user.set_wstate({"bull": query.message.message_id})

        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard,
        )
    else:
        if balance["bull"] < MIN_WITHDRAW_bull and user.get_address():
            await query.answer(
                text=f"⚠ Минимальная сумма вывода {MIN_WITHDRAW_bull} $BULL ({round(MIN_WITHDRAW_bull * course(), 3)}$)",
                show_alert=True,
            )
        if not user.get_address():
            await query.answer(
                text=f"⚠️ Для того, чтобы вывести $BULL нужно привязать кошелёк!",
                show_alert=True,
            )


@app.callback_query(F.data.startswith("verify_withdraw_"))
async def withdraw_sum_callback(query: CallbackQuery):
    user_id = query.from_user.id
    coin = query.data.split("_")[2]
    amount = float(query.data.split("_")[3])
    user = User(user_id)

    user.set_name(query.from_user.username)
    address = user.get_address()
    usd = "(<i>" + str(round(amount * course(), 3)) + "$</i>) "
    markup = [
        [
            InlineKeyboardButton(
                text=f"💸 Вывести {amount} ${coin.upper()}",
                callback_data=f"withdraw_{coin}_{amount}",
            )
        ],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back_withdraw")],
    ]
    text = f"💸 Отправить {amount} ${coin.upper()} {usd}на кошелёк в {await get_app_name(user_id)}"
    if not address:
        text = f"⚠️ Для того, чтобы вывести ${coin.upper()} нужно привязать кошелёк!"
        await query.answer(text=text, show_alert=True)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard,
        )


@app.callback_query(F.data.startswith("withdraw_"))
async def withdraw_success_callback(query: CallbackQuery):
    user_id = query.from_user.id
    sub = await check_sub(user_id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await query.answer(text=text, show_alert=True)
    else:
        coin = query.data.split("_")[1]
        amount = float(query.data.split("_")[2])
        user = User(user_id)

        user.set_name(query.from_user.username)

        if coin == "bull":
            await query.message.edit_text(
                "💰 Подтвердите что вы человек: нажмите <b>'Проверить'</b>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Проверить",
                                callback_data=f"search_withdraw_{amount}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="⬅ Назад", callback_data="back_withdraw"
                            )
                        ],
                    ]
                ),
            )


@app.callback_query(F.data.startswith("search_withdraw_"))
async def check_withdraw_callback(query: CallbackQuery):
    user_id = query.from_user.id
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=f"💸 Подтвердите транзакцию в {await get_app_name(user_id)} и ожидайте.",
    )

    sub = await check_sub(user_id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await query.answer(text=text, show_alert=True)
    else:
        coin = "bull"
        amount = float(query.data.split("_")[2])
        user = User(user_id)

        user.set_name(query.from_user.username)
        address = user.get_address()
        usd = "(<i>" + str(round(amount * course(), 3)) + "$</i>) "
        text = f"✅ Вы успешно вывели {amount} ${coin.upper()} {usd} на {await get_app_name(user_id)}"
        markup = [
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="wallet"),
            ]
        ]

        transfer_status = None

        tr_jetton = await send_transaction_tonconnect(user_id)

        if tr_jetton == True:
            transfer_status = await TransferJetton(
                bull_MASTER_ADDRESS, address, round(float(amount), 2)
            )

        if transfer_status == None:
            await query.message.edit_text(
                f"💬 Вы отклонили транзакцию в {await get_app_name(user_id)}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⬅ Назад", callback_data="back_withdraw"
                            )
                        ]
                    ]
                ),
            )
        elif transfer_status == False:
            await query.message.edit_text(
                "❌ При выводе $BULL произошла ошибка, $TON вернутся на ваш кошелёк",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⬅ Назад", callback_data="back_withdraw"
                            )
                        ]
                    ]
                ),
            )
        else:
            balance = user.get_balance()
            balance[coin] = balance[coin] - float(amount)
            user.set_balance(balance)

            keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

            await bot.edit_message_text(
                chat_id=user_id,
                message_id=query.message.message_id,
                text=text,
                reply_markup=keyboard,
            )


@app.callback_query(F.data == "back_withdraw")
async def back_withdraw_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)

    user.set_name(query.from_user.username)
    text = f"❌ Отмена "
    markup = [[InlineKeyboardButton(text="⬅ Назад", callback_data="wallet")]]
    user.set_wstate({"bull": 0})

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=keyboard,
    )


@app.callback_query(F.data == "connect")
async def connect_shoosee_callback(query: CallbackQuery):
    user_id = query.from_user.id
    text = "🔗 Выберите кошелёк из списка:"

    markup = []

    for wallet in wallet_list:
        markup.append(
            [
                InlineKeyboardButton(
                    text=f"👛 {wallet['name']}",
                    callback_data=f"connect:{wallet['name']}",
                )
            ]
        )

    markup.append(
        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="wallet"),
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=keyboard,
    )


@app.callback_query(F.data == "disconnect")
async def disconnect_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)

    user.set_name(query.from_user.username)
    text = "✅ Адрес успешно отвязан!"

    await disconnect_wallet(user_id)
    user.set_address("''")

    await wallet_callback(query)

    await query.answer(text=text, show_alert=True)


@app.callback_query(F.data.startswith("connect:"))
async def connect_callback(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)

    user.set_name(query.from_user.username)
    wallet = query.data.split(":")[1]
    url, connector = await connect_wallet(chat_id=user_id, wallet_name=wallet)
    text = f"🔗 Перейдите по ссылке для подключения {wallet}:"
    markup = [
        [InlineKeyboardButton(text="👛 Подключить", url=url)],
        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="wallet"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=keyboard,
    )

    result = await wait_connection(connector)
    markup = [
        [InlineKeyboardButton(text="⬅ Назад", callback_data="wallet")],
    ]
    if result == f"Timeout error!":
        text = "❎ Время ожидания вышло, попробуйте ещё раз!"
    else:
        user.set_address(f"'{result}'")
        text = f"✅ Кошелёк <code>{result}</code> успешно подключен!"

    keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=keyboard,
    )
