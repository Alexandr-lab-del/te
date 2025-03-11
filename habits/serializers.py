from rest_framework import serializers
from .models import Habit
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class HabitSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Habit
        fields = '__all__'

    def validate(self, data):
        reward = data.get('reward')
        related_habit = data.get('related_habit')
        is_enjoyable = data.get('is_enjoyable')

        if reward and related_habit:
            raise serializers.ValidationError(
                "Вы не можете одновременно указать и 'reward', и 'related_habit'. Выберите одно из них."
            )

        if related_habit:
            if not related_habit.is_enjoyable:
                raise serializers.ValidationError(
                    "Указанная привычка в 'related_habit' должна быть приятной (is_enjoyable=True)."
                )

        if is_enjoyable:
            if reward or related_habit:
                raise serializers.ValidationError(
                    "Параметр 'is_enjoyable' не может быть установлен одновременно с 'reward' или 'related_habit'."
                )

        if data.get('duration') and data['duration'] > 120:
            raise serializers.ValidationError(
                "Время выполнения привычки ('duration') не должно превышать 120 минут."
            )

        periodicity = data.get('periodicity')
        if periodicity and (periodicity < 1 or periodicity > 7):
            raise serializers.ValidationError(
                "Поле 'periodicity' должно быть в диапазоне от 1 до 7 дней."
            )

        return data
