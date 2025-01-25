from celery import shared_task
from .telegram_bot import send_reminder
from .models import Habit


@shared_task
def send_habit_reminder(habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user
        chat_id = user.profile.telegram_chat_id
        message = f"Напоминание: {habit.action} в {habit.time} в {habit.location}"
        send_reminder(chat_id, message)
    except Habit.DoesNotExist:
        pass
