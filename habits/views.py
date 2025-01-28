from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from .models import Habit
from .serializers import HabitSerializer
from .telegram_bot import send_reminder
from rest_framework.exceptions import NotFound


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

    def retrieve(self, request, *args, **kwargs):
        habit = self.get_object()
        if not habit.is_public and habit.user != request.user:
            raise NotFound("Habit not found.")
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise NotFound("Habit not found.")
        serializer.save()

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        chat_id = self.request.user.profile.telegram_chat_id
        message = f"Новое хобби создано: {habit.name}!"

        if chat_id:
            try:
                send_reminder(chat_id, message)
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise NotFound("Habit not found.")
        super().perform_destroy(instance)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        public_habits = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)


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
