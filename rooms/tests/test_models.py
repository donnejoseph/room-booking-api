import pytest
from django.utils import timezone
from datetime import timedelta, time
from rooms.models import Room
from bookings.models import Booking
from django.db import IntegrityError


@pytest.mark.django_db
class TestRoomModel:
    """Test suite for the Room model."""

    def test_room_creation(self):
        """Test creating a room with all required fields."""
        room = Room.objects.create(
            name="Meeting Room A",
            capacity=10,
            floor=3
        )
        
        assert room.name == "Meeting Room A"
        assert room.capacity == 10
        assert room.floor == 3
        assert room.created_at is not None
        assert room.updated_at is not None
        
    def test_room_str_representation(self):
        """Test the string representation of Room."""
        room = Room.objects.create(
            name="Meeting Room B",
            capacity=15,
            floor=2
        )
        
        expected_str = f"Meeting Room B (Floor 2, Capacity: 15)"
        assert str(room) == expected_str
        
    def test_room_unique_name_constraint(self):
        """Test that room names must be unique."""
        # Create a room
        Room.objects.create(
            name="Unique Room",
            capacity=8,
            floor=1
        )
        
        # Try to create another room with the same name
        with pytest.raises(IntegrityError):
            Room.objects.create(
                name="Unique Room",
                capacity=12,
                floor=4
            )
            
    def test_room_is_available_no_bookings(self, room):
        """Test availability checking when there are no bookings."""
        today = timezone.now().date()
        start = time(10, 0)
        end = time(11, 0)
        
        # Room should be available
        assert room.is_available(today, start, end) is True
        
    def test_room_is_available_with_non_overlapping_booking(self, room, user):
        """Test availability checking with a booking that doesn't overlap."""
        today = timezone.now().date()
        
        # Create a booking from 9:00 to 10:00
        Booking.objects.create(
            user=user,
            room=room,
            date=today,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        
        # Check if room is available from 10:00 to 11:00
        assert room.is_available(today, time(10, 0), time(11, 0)) is True
        
    def test_room_is_not_available_with_overlapping_booking(self, room, user):
        """Test availability checking with an overlapping booking."""
        today = timezone.now().date()
        
        # Create a booking from 10:00 to 11:00
        Booking.objects.create(
            user=user,
            room=room,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        # Check overlapping cases
        # Case 1: Completely overlapping (9:30 - 11:30)
        assert room.is_available(today, time(9, 30), time(11, 30)) is False
        
        # Case 2: Start time during existing booking (10:30 - 11:30)
        assert room.is_available(today, time(10, 30), time(11, 30)) is False
        
        # Case 3: End time during existing booking (9:30 - 10:30)
        assert room.is_available(today, time(9, 30), time(10, 30)) is False
        
        # Case 4: Completely containing existing booking (9:30 - 12:00)
        assert room.is_available(today, time(9, 30), time(12, 0)) is False
        
    def test_room_is_available_different_date(self, room, user):
        """Test availability checking on a different date."""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Create a booking for today
        Booking.objects.create(
            user=user,
            room=room,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        # Room should be available tomorrow at the same time
        assert room.is_available(tomorrow, time(10, 0), time(11, 0)) is True
        
    def test_room_ordering(self):
        """Test that rooms are ordered by floor and then name."""
        # Create rooms in a specific order
        room3 = Room.objects.create(name="C Room", floor=2, capacity=5)
        room1 = Room.objects.create(name="A Room", floor=1, capacity=10)
        room2 = Room.objects.create(name="B Room", floor=1, capacity=15)
        room4 = Room.objects.create(name="D Room", floor=3, capacity=20)
        
        # Get rooms in order
        rooms = list(Room.objects.all())
        
        # They should be ordered by floor, then by name
        assert rooms[0] == room1  # Floor 1, "A Room"
        assert rooms[1] == room2  # Floor 1, "B Room" 
        assert rooms[2] == room3  # Floor 2, "C Room"
        assert rooms[3] == room4  # Floor 3, "D Room" 