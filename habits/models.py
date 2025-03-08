from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
from rest_framework.exceptions import NotFound


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    time = models.TimeField(null=True, blank=True)
    action = models.CharField(max_length=255)
    is_enjoyable = models.BooleanField(default=False)
    related_habit = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    periodicity = models.PositiveIntegerField(default=1)
    reward = models.CharField(max_length=255, null=True, blank=True)
    duration = models.PositiveIntegerField(default=120)
    is_public = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.action} at {self.time} in {self.location}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(duration__lte=120),
                name='duration_max_120_seconds'
            ),
        ]


@receiver(post_save, sender=Habit)
def create_periodic_task(sender, instance, created, **kwargs):
    if created:
        schedule, _ = IntervalSchedule.objects.get_or_create(every=instance.periodicity, period=IntervalSchedule.DAYS)
        PeriodicTask.objects.create(
            interval=schedule,
            name=f'Habit Reminder {instance.id}',
            task='habits.tasks.send_habit_reminder',
            args=json.dumps([instance.id]),
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
