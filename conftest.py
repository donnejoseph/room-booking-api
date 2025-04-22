import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rooms.models import Room
from bookings.models import Booking
from django.utils import timezone
from datetime import time

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a regular user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_user(
        username="adminuser",
        email="admin@example.com",
        password="adminpassword",
        is_staff=True
    )


@pytest.fixture
def room():
    """Create a test room."""
    return Room.objects.create(
        name="Test Room",
        capacity=10,
        floor=2
    )


@pytest.fixture
def booking(room, user):
    """Create a test booking for today."""
    today = timezone.now().date()
    return Booking.objects.create(
        user=user,
        room=room,
        date=today,
        start_time=time(10, 0),
        end_time=time(11, 0)
    ) 