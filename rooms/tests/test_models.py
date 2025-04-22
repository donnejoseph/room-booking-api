import pytest
from django.utils import timezone
from datetime import date, time, timedelta
from rooms.models import Room
from bookings.models import Booking
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.rooms
@pytest.mark.unit
class TestRoomModel:
    """Tests for Room model."""
    
    @pytest.fixture
    def room(self):
        """Create a test room."""
        return Room.objects.create(
            name="Test Room",
            capacity=10,
            floor=2
        )
        
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
    @pytest.fixture
    def booking(self, room, user):
        """Create a test booking for today."""
        today = timezone.now().date()
        return Booking.objects.create(
            user=user,
            room=room,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
    
    def test_room_creation(self, room):
        """Test Room instance creation."""
        assert room.name == "Test Room"
        assert room.capacity == 10
        assert room.floor == 2
        assert str(room) == "Test Room (Floor 2, Capacity: 10)"
        
    def test_room_is_available_no_bookings(self, room):
        """Test room availability when there are no bookings."""
        today = timezone.now().date()
        assert room.is_available(today, time(10, 0), time(11, 0)) is True
        
    def test_room_is_available_with_booking(self, room, booking):
        """Test room availability when there is a booking."""
        today = timezone.now().date()
        
        # Room should not be available during booking time
        assert room.is_available(today, time(9, 30), time(10, 30)) is False
        assert room.is_available(today, time(10, 30), time(11, 30)) is False
        assert room.is_available(today, time(9, 30), time(11, 30)) is False
        
        # Room should be available outside booking time
        assert room.is_available(today, time(8, 0), time(9, 0)) is True
        assert room.is_available(today, time(12, 0), time(13, 0)) is True
        
        # Room should be available on a different date
        tomorrow = today + timedelta(days=1)
        assert room.is_available(tomorrow, time(10, 0), time(11, 0)) is True 