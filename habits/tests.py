from django.test import TestCase
from django.contrib.auth.models import User
from .models import Habit
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch


class HabitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', password='testpass1')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2')

        self.client.force_authenticate(user=self.user1)

        self.habit1 = Habit.objects.create(
            user=self.user1,
            name='Test Habit 1',
            location='Home',
            time='08:00',
            action='play',
            is_enjoyable=False,
            periodicity=1,
            reward='money',
            duration=120,
            is_public=True
        )

        self.habit2 = Habit.objects.create(
            user=self.user2,
            name='Test Habit 2',
            location='Office',
            time='09:00',
            action='work',
            is_enjoyable=True,
            periodicity=3,
            reward='money',
            duration=90,
            is_public=False
        )

    def test_get_habit_detail(self):
        url = reverse('habit-detail', args=[self.habit1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.habit1.name)

    def test_get_habit_detail_forbidden(self):
        url = reverse('habit-detail', args=[self.habit2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_habit(self):
        url = reverse('habit-detail', args=[self.habit1.id])
        data = {'name': 'Updated Habit', 'location': 'Gym'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.name, 'Updated Habit')
        self.assertEqual(self.habit1.location, 'Gym')

    def test_update_habit_forbidden(self):
        url = reverse('habit-detail', args=[self.habit2.id])
        data = {"name": "Updated Habit 2"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_delete_habit(self):
        url = reverse('habit-detail', args=[self.habit1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit1.id).exists())

    def test_delete_habit_forbidden(self):
        url = reverse('habit-detail', args=[self.habit2.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_public_habits(self):
        url = reverse('habit-public')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.habit1.name)

    def test_permissions_for_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('habit-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_habit(self):
        data = {
            'name': 'New Test Habit',
            'location': 'Park',
            'time': '07:00:00',
            'action': 'Walk',
            'is_enjoyable': True,
            'reward': '',
            'duration': 60,
            'is_public': True,
            'periodicity': 2
        }
        response = self.client.post(reverse('habit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.filter(user=self.user1).count(), 2)

    def test_get_habit_with_pagination(self):
        for i in range(10):
            Habit.objects.create(
                user=self.user1,
                name=f'Habit {i + 3}',
                location='Planet',
                time='10:00:00',
                action='anything',
                periodicity=1,
                duration=30
            )
        response = self.client.get(reverse('habit-list') + '?page_size=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_create_habit_invalid_related_habit(self):
        habit_related = Habit.objects.create(
            user=self.user1,
            name='Unenjoyable Habit',
            location='Work',
            time='12:00:00',
            action='Test Action',
            is_enjoyable=False
        )
        data = {
            'name': 'New Test Habit',
            'location': 'Park',
            'time': '07:00:00',
            'action': 'Walk',
            'is_enjoyable': True,
            'reward': '',
            'duration': 60,
            'is_public': True,
            'periodicity': 2,
            'related_habit': habit_related.id
        }
        response = self.client.post(reverse('habit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_delete_other_users_habit(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('habit-detail', args=[self.habit1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Habit.objects.filter(id=self.habit1.id).exists())

    def test_create_habit_minimal_fields(self):
        data = {
            'name': 'Minimal Test Habit',
            'location': 'Nowhere',
            'action': 'Do Nothing',
            'periodicity': 1,
            'duration': 10
        }
        response = self.client.post(reverse('habit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        habit = Habit.objects.get(name='Minimal Test Habit')
        self.assertEqual(habit.user, self.user1)

    def test_get_public_habit_other_user(self):
        self.habit2.is_public = True
        self.habit2.save()
        url = reverse('habit-detail', args=[self.habit2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.habit2.name)

    @patch('habits.views.send_reminder')
    def test_create_habit_with_telegram_notification(self, mock_send_reminder):
        self.user1.profile.telegram_chat_id = '123456789'
        self.user1.profile.save()
        data = {
            'name': 'Notify Habit',
            'location': 'Everywhere',
            'time': '06:00:00',
            'action': 'Wake Up',
            'periodicity': 1,
            'duration': 10,
        }
        response = self.client.post(reverse('habit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_reminder.assert_called_once_with('123456789', 'Новое хобби создано: Notify Habit!')

    def test_create_habit_with_reward_and_related_habit(self):
        related_habit = Habit.objects.create(
            user=self.user1,
            name='Related Habit',
            location='Somewhere',
            action='Do something enjoyable',
            is_enjoyable=True
        )
        data = {
            'name': 'Conflicting Habit',
            'location': 'Library',
            'time': '11:00:00',
            'action': 'Study',
            'is_enjoyable': False,
            'reward': 'Have coffee',
            'duration': 100,
            'is_public': True,
            'periodicity': 3,
            'related_habit': related_habit.id
        }
        response = self.client.post(reverse('habit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_create_enjoyable_habit_with_reward(self):
        data = {
            'name': 'Enjoyable Habit with Reward',
            'location': 'Park',
            'time': '08:30:00',
            'action': 'Jogging',
            'is_enjoyable': True,
            'reward': 'Watch TV',
            'duration': 50,
            'is_public': False,
            'periodicity': 1
        }
        response = self.client.post(reverse('habit-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_update_public_habit_of_other_user(self):
        self.habit2.is_public = True
        self.habit2.save()
        url = reverse('habit-detail', args=[self.habit2.id])
        data = {'name': 'Attempted Update'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        self.habit2.refresh_from_db()
        self.assertNotEqual(self.habit2.name, 'Attempted Update')
