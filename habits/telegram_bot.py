import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.contrib.auth.models import User


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


application_django = get_wsgi_application()


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


async def send_reminder(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.chat.username

    user, created = User.objects.get_or_create(username=username, defaults={"password": "telegram_default_password"})

    if created:
        await update.message.reply_text(
            "Привет! Я зарегистрировал тебя как нового пользователя. Ты можешь добавлять свои привычки."
        )
    else:
        await update.message.reply_text("Добро пожаловать обратно! Я твой помощник для отслеживания привычек.")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    username = update.message.chat.username

    try:
        user = User.objects.get(username=username)

        user.profile.telegram_chat_id = chat_id
        user.profile.save()

        await update.message.reply_text("Ты успешно подписался на уведомления!")
    except User.DoesNotExist:
        await update.message.reply_text("Не удается найти пользователя. Сначала напиши /start.")


async def habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.chat.username
    try:
        user = User.objects.get(username=username)
        habit_list = user.habits.all()
        if habit_list.exists():
            response = "Вот твои привычки:\n"
            for idx, habit in enumerate(habit_list, start=1):
                response += (
                    f"{idx}. {habit.action} в {habit.time} ({habit.location})\n"
                )
        else:
            response = "У тебя пока нет привычек. Добавь свои привычки через веб-приложение!"
    except User.DoesNotExist:
        response = "Не удается найти пользователя. Сначала напиши /start."
    await update.message.reply_text(response)


async def reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.chat.username
    try:
        user = User.objects.get(username=username)
        chat_id = user.profile.telegram_chat_id
        habit_list = user.habits.all()

        if habit_list.exists():
            for habit in habit_list:
                message = f"Напоминание: {habit.action} в {habit.time} в {habit.location}"
                await send_reminder(chat_id, message)
            await update.message.reply_text("Все напоминания отправлены!")
        else:
            await update.message.reply_text("У тебя пока нет привычек для напоминаний.")
    except User.DoesNotExist:
        await update.message.reply_text("Не удается найти пользователя. Сначала напиши /start.")
    except AttributeError:
        await update.message.reply_text("Ты ещё не подписался на уведомления. Напиши /subscribe.")


def main():

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("habits", habits))
    application.add_handler(CommandHandler("reminders", reminders))

    print("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
