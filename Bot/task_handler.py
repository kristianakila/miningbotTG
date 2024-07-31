from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .cfg import *
from .user import User
from .get_course_bull import readcource as course
from .task import Task

import logging

logging.basicConfig(level=logging.INFO, filename="log.log")

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


async def check_user_completed_task(user_id, channels):
    try:
        sub_list = ["member", "administrator", "creator"]
        for i in channels:
            if "*" in i:
                i = i.split("*")[0]
            _ = await bot.get_chat_member(i, user_id)
            if _.status.name.lower() not in sub_list:
                return False
        return True
    except Exception as e:
        logging.error(e)
        return False


async def get_tasks(query: CallbackQuery):
    user_id = query.from_user.id
    user = User(user_id)
    user.add_user(None)

    user.set_name(query.from_user.username)
    tasks = Task.select_all_tasks()

    if not tasks:
        await query.answer("📋 На данный момент нет заданий!", show_alert=True)
        return

    keyboard = []
    for task in tasks:
        task_instance = Task(task[0])
        if str(user_id) not in task_instance.get_info()["users_completed"]:
            btntext = f"⚡  {task_instance.get_info()['completions']}/{task_instance.get_info()['max_completions']} - 💰 {task_instance.get_info()['price_per_completion']} $BULL"
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=btntext,
                        callback_data=f"task_{task[0]}",
                    )
                ]
            )
        elif user_id in admin_list:
            btntext = f"✅ {task_instance.get_info()['completions']}/{task_instance.get_info()['max_completions']} - 💰 {task_instance.get_info()['price_per_completion']} $BULL"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=btntext,
                        callback_data=f"task_{task[0]}",
                    )
                ]
            )

    if not keyboard:
        await query.answer("📋 Вы уже выполнили все задания!", show_alert=True)
        return

    keyboard.append(
        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
        ]
    )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    text = "📋 Выберите задание из списка:"

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=query.message.message_id,
        text=text,
        reply_markup=reply_markup,
    )


async def task_button(query: CallbackQuery):
    user_id = query.from_user.id
    task_id = int(query.data.split("_")[1])
    task = Task(task_id)
    task_info = task.get_info()

    channels = "\n".join(
        [
            f"{idx + 1}. {channel if not '*' in channel else channel.split('*')[1]}"
            for idx, channel in enumerate(task_info["channels"])
        ]
    )
    message = (
        # f"📋 Описание:\n<i>{task_info['description']}</i>\n\n"
        f"💰 Награда за выполнение {task_info['price_per_completion']} $BULL\n\n"
        f"⚡ Выполнено {task_info['completions']} из {task_info['max_completions']}\n\n"
        f"💬 Подписаться:\n{channels}"
    )

    keyboard = [
        [InlineKeyboardButton(text="⚡ Проверить", callback_data=f"check_{task_id}")]
    ]
    keyboard.append(
        [
            InlineKeyboardButton(text="⬅ Назад", callback_data="tasks"),
        ]
    )
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await query.message.edit_text(text=message, reply_markup=reply_markup)


async def check_completion(query: CallbackQuery):
    user_id = query.from_user.id
    task_id = int(query.data.split("_")[1])
    task = Task(task_id)
    task_info = task.get_info()

    if str(user_id) in task_info["users_completed"]:
        await query.answer("📋 Вы уже выполнили это задание!", show_alert=True)
        return

    user = User(user_id)

    user.set_name(query.from_user.username)
    if await check_user_completed_task(user_id, task_info["channels"]):
        task.add_user_completed(user_id)
        task.set_completions(task_info["completions"] + 1)

        if task_info["completions"] + 1 >= task_info["max_completions"]:
            Task.delete_task(task_id)

        await query.answer(text=f"📋 Задание выполнено!", show_alert=True)

        user.set_balance(
            {"bull": user.get_balance()["bull"] + task_info["price_per_completion"]}
        )

        text = f"💰 Вы получили {task_info['price_per_completion']} $BULL"
        markup = [
            [
                InlineKeyboardButton(text="⬅ Назад", callback_data="back"),
            ]
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=markup)

        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard,
        )
    else:
        await query.answer(text=f"💔 Вы не подписались на все каналы!", show_alert=True)


@app.callback_query(F.data == "tasks")
async def process_tasks_callback(callback_query: CallbackQuery):
    sub = await check_sub(callback_query.from_user.id)
    if not sub:
        text = f"⚠ Для того, чтобы пользоваться ботом нужно подписаться на\n\n1. @NFTBullTon\n2. @NFTBullChat\n\nИ снова ввести /start"
        await callback_query.answer(text=text, show_alert=True)
    else:
        await get_tasks(callback_query)


@app.callback_query(F.data.startswith("task_"))
async def process_task_callback(callback_query: CallbackQuery):
    await task_button(callback_query)


@app.callback_query(F.data.startswith("check_"))
async def process_check_callback(callback_query: CallbackQuery):
    await check_completion(callback_query)
