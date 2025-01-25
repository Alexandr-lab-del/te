from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, RegisterView

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('public-habits/', HabitViewSet.as_view({'get': 'public'}), name='public-habits'),
    path('register/', RegisterView.as_view(), name='register'),
]
