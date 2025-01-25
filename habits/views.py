from rest_framework import viewsets, permissions
from .models import Habit
from .serializers import HabitSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from .telegram_bot import send_reminder
from rest_framework.permissions import IsAuthenticated


class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public
        return obj.user == request.user


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = HabitPagination

    def get_queryset(self):
        if self.action == 'list':
            return self.request.user.habits.all()
        elif self.action == 'public':
            return Habit.objects.filter(is_public=True)
        return Habit.objects.all()

    def perform_create(self, serializer):

        habit = serializer.save(user=self.request.user)

        chat_id = self.request.user.profile.telegram_chat_id
        message = f"Новое хобби создано: {habit.name}!"

        if chat_id:
            try:
                send_reminder(chat_id, message)
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
