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
            raise serializers.ValidationError("Нельзя одновременно указывать reward и related_habit.")

        if related_habit and not related_habit.is_enjoyable:
            raise serializers.ValidationError("related_habit должна быть (is_enjoyable=True).")

        if is_enjoyable and (reward or related_habit):
            raise serializers.ValidationError("is_enjoyable не может иметь reward или related_habit.")

        if data.get('duration') > 120:
            raise serializers.ValidationError("Время на выполнение привычки нужно уменьшить.")

        periodicity = data.get('periodicity')
        if periodicity < 1 or periodicity > 7:
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней.")

        return data
