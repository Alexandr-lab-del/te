from django.test import TestCase
from django.contrib.auth.models import User
from .models import Habit
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


class HabitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.habit = Habit.objects.create(
            user=self.user,
            location='Home',
            name='Home',
            time='08:00',
            action='Meditate',
            is_enjoyable=False,
            periodicity=1,
            reward='Read a book',
            duration=120,
            is_public=True
        )

    def test_create_habit(self):
        data = {
            'location': 'Office',
            'name': 'Office',
            'time': '09:00',
            'action': 'Exercise',
            'is_enjoyable': False,
            'periodicity': 1,
            'reward': 'Watch a movie',
            'duration': 120,
            'is_public': False
        }
        response = self.client.post(reverse('habit-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_habits(self):
        response = self.client.get(reverse('habit-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_public_habits(self):
        response = self.client.get(reverse('public-habits'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
