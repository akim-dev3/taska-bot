import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from database import init_db, add_task, get_tasks, complete_task, delete_task, clear_done, get_stats

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    name = message.from_user.first_name
    await message.answer(
        f"Hey {name}! I'm Taska — your personal task manager.\n\n"
        "Commands:\n"
        "/add <task> — add a new task\n"
        "/list — show active tasks\n"
        "/done — show completed tasks\n"
        "/stats — your progress summary\n"
        "/cleardone — delete all completed tasks\n"
        "/help — show this message"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await start(message)


@dp.message(Command("add"))
async def add(message: Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2 or not args[1].strip():
        await message.answer("Usage: /add <task text>\nExample: /add Buy groceries")
        return

    text = args[1].strip()

    if len(text) > 280:
        await message.answer("Task text is too long. Keep it under 280 characters.")
        return

    task_id = add_task(user_id, text)
    await message.answer(f"Task #{task_id} added:\n{text}")


@dp.message(Command("list"))
async def list_tasks(message: Message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id, done=0)

    if not tasks:
        await message.answer("No active tasks. Add one with /add <task>")
        return

    lines = ["Your active tasks:\n"]
    buttons = []

    for task_id, text, _ in tasks:
        lines.append(f"#{task_id} {text}")
        buttons.append([
            InlineKeyboardButton(text=f"✓ Done #{task_id}", callback_data=f"done:{task_id}"),
            InlineKeyboardButton(text=f"✕ Delete #{task_id}", callback_data=f"delete:{task_id}"),
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("\n".join(lines), reply_markup=markup)


@dp.message(Command("done"))
async def done_list(message: Message):
    user_id = message.from_user.id
    tasks = get_tasks(user_id, done=1)

    if not tasks:
        await message.answer("No completed tasks yet.")
        return

    lines = [f"Completed tasks ({len(tasks)}):\n"]
    for task_id, text, _ in tasks:
        lines.append(f"✓ #{task_id} {text}")
    lines.append("\nUse /cleardone to remove all completed tasks.")
    await message.answer("\n".join(lines))


@dp.message(Command("stats"))
async def stats(message: Message):
    user_id = message.from_user.id
    data = get_stats(user_id)
    total = data["pending"] + data["completed"]

    if total == 0:
        await message.answer("No tasks yet. Start with /add <task>")
        return

    rate = int(data["completed"] / total * 100)
    bar_filled = min(rate // 10, 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)

    await message.answer(
        f"Your progress:\n\n"
        f"Active:    {data['pending']}\n"
        f"Completed: {data['completed']}\n"
        f"Total:     {total}\n\n"
        f"{bar} {rate}% done"
    )


@dp.message(Command("cleardone"))
async def clear_done_command(message: Message):
    user_id = message.from_user.id
    count = clear_done(user_id)

    if count == 0:
        await message.answer("No completed tasks to clear.")
    else:
        await message.answer(f"Cleared {count} completed task(s).")


@dp.callback_query(F.data.startswith("done:"))
async def callback_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_id = int(callback.data.split(":")[1])
    success = complete_task(user_id, task_id)

    if success:
        await callback.message.edit_text(f"Task #{task_id} marked as done.")
    else:
        await callback.message.edit_text(f"Task #{task_id} not found or already done.")
    await callback.answer()


@dp.callback_query(F.data.startswith("delete:"))
async def callback_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_id = int(callback.data.split(":")[1])
    success = delete_task(user_id, task_id)

    if success:
        await callback.message.edit_text(f"Task #{task_id} deleted.")
    else:
        await callback.message.edit_text(f"Task #{task_id} not found.")
    await callback.answer()


async def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set in .env")
    init_db()
    logger.info("Bot started")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
