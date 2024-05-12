from pytz import timezone

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command

from app import tasks
from app.tables import products as pt
from app.tables import employees as et
from app.config import products_config, employees_config, telegram_config

bot = Bot(
    token=telegram_config['TOKEN'],
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

scheduler = AsyncIOScheduler()
products_task = scheduler.add_job(
    tasks.products,
    'interval',
    seconds=products_config['sending_timeout'],
    args=(
        bot,
        telegram_config['products_chat_id'],
        products_config,
        pt.get_data,
    )
)
employees_task = scheduler.add_job(
    tasks.employees,
    'cron',
    day_of_week='mon',
    hour=8,
    minute=0,
    second=0,
    timezone=timezone('America/Bogota'),
    args=(
        bot,
        telegram_config['employees_chat_ids'],
        employees_config,
        et.get_data
    )
)


@dp.message(Command('id'))
async def id(message: Message) -> None:
    await message.answer(f'This chat id is {html.code(message.chat.id)}')


@dp.message(Command('bill'))
async def bill(message: Message) -> None:
    await tasks.employees(
        bot,
        telegram_config['employees_chat_ids'],
        employees_config,
        et.get_data
    )


@dp.message(Command('start_products'))
async def start_products(message: Message) -> None:
    if message.chat.id != telegram_config['products_chat_id']:
        return

    global products_task
    products_task = scheduler.add_job(
        tasks.products,
        'interval',
        seconds=products_config['sending_timeout'],
        args=(
            bot,
            telegram_config['products_chat_id'],
            products_config,
            pt.get_data,
        )
    )
    scheduler.start()

    await message.answer('Products loop has started')


@dp.message(Command('stop_products'))
async def stop_products(message: Message) -> None:
    if message.chat.id != telegram_config['products_chat_id']:
        return

    global products_task
    if products_task:
        products_task.remove()

    await message.answer('Products loop has stopped')


@dp.message(Command('start_employees'))
async def start_employees(message: Message) -> None:
    if message.chat.id != telegram_config['products_chat_id']:
        return

    global employees_task
    employees_task = scheduler.add_job(
        tasks.employees,
        'interval',
        seconds=20,
        args=(
            bot,
            telegram_config['employees_chat_ids'],
            employees_config,
            et.get_data,
        )
    )
    scheduler.start()

    await message.answer('Employees loop has started')


@dp.message(Command('stop_employees'))
async def stop_employees(message: Message) -> None:
    if message.chat.id != telegram_config['products_chat_id']:
        return

    global employees_task
    if employees_task:
        employees_task.remove()

    await message.answer('Employees loop has stopped')


async def main() -> None:
    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
