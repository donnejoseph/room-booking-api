import pytest
from django.utils import timezone
from datetime import date, time, timedelta
from rooms.models import Room
from bookings.models import Booking
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.bookings
@pytest.mark.unit
class TestBookingModel:
    """Tests for Booking model."""
    
    @pytest.fixture
    def room(self):
        """Create a test room."""
        return Room.objects.create(
            name="Test Room",
            capacity=10,
            floor=2
        )
        
    @pytest.fixture
    def another_room(self):
        """Create another test room."""
        return Room.objects.create(
            name="Another Room",
            capacity=5,
            floor=1
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
    
    def test_booking_creation(self, booking, room, user):
        """Test Booking instance creation."""
        today = timezone.now().date()
        assert booking.user == user
        assert booking.room == room
        assert booking.date == today
        assert booking.start_time == time(10, 0)
        assert booking.end_time == time(11, 0)
        
    def test_booking_str(self, booking):
        """Test Booking string representation."""
        today = timezone.now().date()
        expected_str = f"Test Room - {today} 10:00:00 to 11:00:00 (by testuser)"
        assert str(booking) == expected_str
        
    def test_booking_clean_valid(self, room, user):
        """Test Booking validation with valid data."""
        today = timezone.now().date()
        booking = Booking(
            user=user,
            room=room,
            date=today,
            start_time=time(12, 0),
            end_time=time(13, 0)
        )
        booking.clean()  # Should not raise any exceptions
        
    def test_booking_clean_past_date(self, room, user):
        """Test Booking validation with past date."""
        yesterday = timezone.now().date() - timedelta(days=1)
        booking = Booking(
            user=user,
            room=room,
            date=yesterday,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        with pytest.raises(ValidationError) as exc:
            booking.clean()
        assert 'date' in str(exc.value)
        
    def test_booking_clean_end_time_before_start_time(self, room, user):
        """Test Booking validation with end time before start time."""
        today = timezone.now().date()
        booking = Booking(
            user=user,
            room=room,
            date=today,
            start_time=time(11, 0),
            end_time=time(10, 0)
        )
        
        with pytest.raises(ValidationError) as exc:
            booking.clean()
        assert 'end_time' in str(exc.value)
        
    def test_booking_clean_overlapping_room_booking(self, room, user, booking):
        """Test Booking validation with overlapping room booking."""
        today = timezone.now().date()
        new_booking = Booking(
            user=user,
            room=room,
            date=today,
            start_time=time(10, 30),
            end_time=time(11, 30)
        )
        
        with pytest.raises(ValidationError) as exc:
            new_booking.clean()
        assert 'non_field_errors' in str(exc.value)
        
    def test_booking_clean_overlapping_user_booking(self, another_room, user, booking):
        """Test Booking validation with overlapping user booking."""
        today = timezone.now().date()
        new_booking = Booking(
            user=user,
            room=another_room,
            date=today,
            start_time=time(10, 30),
            end_time=time(11, 30)
        )
        
        with pytest.raises(ValidationError) as exc:
            new_booking.clean()
        assert 'non_field_errors' in str(exc.value) 