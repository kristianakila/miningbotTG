from bot.task import Task
from bot.user import User
from bot.cfg import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import time

task = Task(task_id=0)


def delete_all():
    Task.drop_all()


def id():
    time_ = int(time.time())
    return time_


async def send(amount):
    users = User.get_all()

    for user in users:
        try:
            if user["user_id"]:
                await bot.send_message(
                    user["user_id"],
                    f"📋 @{user['username']}, новое задание уже доступно!\n\n🔥 Награда {amount} $BULL",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="📋 Задания", callback_data="tasks"
                                )
                            ]
                        ]
                    ),
                )
        except:
            continue


def add():

    d = "Подпишитесь на канал нашего партнёра."
    channels = ["@bestinvestor_cc"]

    task.add_task(
        id=id(),
        price_per_completion=50,
        channels=channels,
        completions=0,
        max_completions=4000,
        description=d,
    )

    
def add1():
    d = "Подпишитесь на канал нашего партнёра."
    channels = ["@atletis_not"]

    task.add_task(
        id=id(),
        price_per_completion=50,
        channels=channels,
        completions=0,
        max_completions=1000,
        description=d,
    )


def delete_by_id():
    id = 1721422136
    Task.delete_task(id)


async def main():
    add()
    print("Task added!")
    await send(50)
    print("Success")
    add1()
    print("Task added!")
    await send(50)
    print("Success")


asyncio.run(main())
