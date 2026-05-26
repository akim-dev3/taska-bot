import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from database import init_db, add_task, get_tasks, complete_task, delete_task, clear_done, get_stats

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    text = (
        f"Hey {name}! I'm Taska — your personal task manager.\n\n"
        "Commands:\n"
        "/add <task> — add a new task\n"
        "/list — show active tasks\n"
        "/done — show completed tasks\n"
        "/stats — your progress summary\n"
        "/cleardone — delete all completed tasks\n"
        "/help — show this message"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Usage: /add <task text>\nExample: /add Buy groceries")
        return

    text = " ".join(context.args).strip()

    if len(text) > 300:
        await update.message.reply_text("Task text is too long. Keep it under 280 characters.")
        return

    task_id = add_task(user_id, text)
    await update.message.reply_text(f"Task #{task_id} added:\n{text}")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id, done=0)

    if not tasks:
        await update.message.reply_text("No active tasks. Add one with /add <task>")
        return

    buttons = []
    lines = ["Your active tasks:\n"]

    for task_id, text, created_at in tasks:
        lines.append(f"#{task_id} {text}")
        buttons.append([
            InlineKeyboardButton(f"✓ Done #{task_id}", callback_data=f"done:{task_id}"),
            InlineKeyboardButton(f"✕ Delete #{task_id}", callback_data=f"delete:{task_id}"),
        ])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("\n".join(lines), reply_markup=reply_markup)


async def done_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = get_tasks(user_id, done=1)

    if not tasks:
        await update.message.reply_text("No completed tasks yet.")
        return

    lines = [f"Completed tasks ({len(tasks)}):\n"]
    for task_id, text, _ in tasks:
        lines.append(f"✓ #{task_id} {text}")

    lines.append("\nUse /cleardone to remove all completed tasks.")
    await update.message.reply_text("\n".join(lines))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = get_stats(user_id)
    total = data["pending"] + data["completed"]

    if total == 0:
        await update.message.reply_text("No tasks yet. Start with /add <task>")
        return

    rate = int(data["completed"] / total * 100) if total > 0 else 0
    bar_filled = rate // 10
    bar_filled = min(bar_filled, 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)

    text = (
        f"Your progress:\n\n"
        f"Active:    {data['pending']}\n"
        f"Completed: {data['completed']}\n"
        f"Total:     {total}\n\n"
        f"{bar} {rate}% done"
    )
    await update.message.reply_text(text)


async def clear_done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = clear_done(user_id)

    if count == 0:
        await update.message.reply_text("No completed tasks to clear.")
    else:
        await update.message.reply_text(f"Cleared {count} completed task(s).")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data.startswith("done:"):
        task_id = int(data.split(":")[1])
        success = complete_task(user_id, task_id)
        if success:
            await query.edit_message_text(f"Task #{task_id} marked as done.")
        else:
            await query.edit_message_text(f"Task #{task_id} not found or already done.")

    elif data.startswith("delete:"):
        task_id = int(data.split(":")[1])
        success = delete_task(user_id, task_id)
        if success:
            await query.edit_message_text(f"Task #{task_id} deleted.")
        else:
            await query.edit_message_text(f"Task #{task_id} not found.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command. Use /help to see available commands.")


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set in .env")

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("done", done_list))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("cleardone", clear_done_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Bot started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
