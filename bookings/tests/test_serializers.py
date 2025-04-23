import pytest
from django.utils import timezone
from datetime import timedelta, time
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rooms.models import Room
from bookings.models import Booking
from bookings.serializers import BookingSerializer
from django.db import models

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.bookings
class TestBookingSerializer:
    """Test suite for BookingSerializer."""

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
            capacity=15,
            floor=3
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
        """Create a test booking."""
        today = timezone.now().date()
        return Booking.objects.create(
            user=user,
            room=room,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
    @pytest.fixture
    def request_factory(self):
        """Return a request factory."""
        return APIRequestFactory()
        
    @pytest.fixture
    def booking_data(self, room):
        """Return valid booking data."""
        today = timezone.now().date()
        return {
            'room_id': room.id,
            'date': today,
            'start_time': '12:00:00',
            'end_time': '13:00:00'
        }
    
    def test_booking_serialization(self, booking, user):
        """Test serializing a booking."""
        # Create a request and context
        request_factory = APIRequestFactory()
        request = request_factory.get('/')
        request.user = user
        
        # Serialize the booking
        serializer = BookingSerializer(booking, context={'request': request})
        
        # Check the serialized data
        data = serializer.data
        assert data['id'] == booking.id
        assert data['date'] == str(booking.date)
        assert data['start_time'] == str(booking.start_time)
        assert data['end_time'] == str(booking.end_time)
        assert data['user']['id'] == user.id
        assert data['user']['username'] == user.username
        assert data['room']['id'] == booking.room.id
        assert data['room']['name'] == booking.room.name
        
    def test_booking_deserialization(self, booking_data, user):
        """Test deserializing booking data."""
        # Create a request and context
        request_factory = APIRequestFactory()
        request = request_factory.post('/')
        request.user = user
        
        # Deserialize the data
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        
        # Check that validation passes
        assert serializer.is_valid(), serializer.errors
        
    def test_validate_past_date(self, booking_data, user):
        """Test validation for booking date in the past."""
        # Set date to yesterday
        yesterday = timezone.now().date() - timedelta(days=1)
        booking_data['date'] = yesterday
        
        # Create request and context
        request_factory = APIRequestFactory()
        request = request_factory.post('/')
        request.user = user
        
        # Check validation fails
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        assert not serializer.is_valid()
        assert 'date' in serializer.errors
        
    def test_validate_end_time_before_start_time(self, booking_data, user):
        """Test validation for end time before start time."""
        # Set end time before start time
        booking_data['start_time'] = '14:00:00'
        booking_data['end_time'] = '13:00:00'
        
        # Create request and context
        request_factory = APIRequestFactory()
        request = request_factory.post('/')
        request.user = user
        
        # Check validation fails
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        assert not serializer.is_valid()
        assert 'end_time' in serializer.errors
        
    def test_validate_room_availability(self, booking, booking_data, user):
        """Test validation for room availability."""
        # Set the booking to overlap with existing booking
        booking_data['date'] = booking.date
        booking_data['start_time'] = '10:30:00'  # Overlaps with 10:00-11:00
        booking_data['end_time'] = '11:30:00'
        booking_data['room_id'] = booking.room.id
        
        # Create request and context
        request_factory = APIRequestFactory()
        request = request_factory.post('/')
        request.user = user
        
        # Check validation fails
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        
    def test_validate_user_availability(self, booking, booking_data, user, another_room):
        """Test validation for user availability."""
        # Set booking for a different room but overlapping time
        booking_data['date'] = booking.date
        booking_data['start_time'] = '10:30:00'  # Overlaps with 10:00-11:00
        booking_data['end_time'] = '11:30:00'
        booking_data['room_id'] = another_room.id
        
        # Create request and context
        request_factory = APIRequestFactory()
        request = request_factory.post('/')
        request.user = user
        
        # Check validation fails
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        
    def test_create_booking(self, booking_data, user):
        """Test creating a booking via serializer."""
        # Create request and context
        request_factory = APIRequestFactory()
        request = request_factory.post('/')
        request.user = user
        
        # Create serializer and validate
        serializer = BookingSerializer(data=booking_data, context={'request': request})
        assert serializer.is_valid(), serializer.errors
        
        # Save the booking
        booking = serializer.save()
        
        # Check the booking was created correctly
        assert booking.user == user
        assert booking.date == booking_data['date']
        assert str(booking.start_time) == booking_data['start_time']
        assert str(booking.end_time) == booking_data['end_time']
        
    def test_update_booking(self, booking, user):
        """Test updating a booking via serializer."""
        # Create update data
        update_data = {
            'date': booking.date,
            'start_time': '13:00:00',
            'end_time': '14:00:00',
            'room_id': booking.room.id
        }
        
        # Create request and context
        request_factory = APIRequestFactory()
        request = request_factory.put('/')
        request.user = user
        
        # Update the booking
        serializer = BookingSerializer(booking, data=update_data, context={'request': request}, partial=True)
        assert serializer.is_valid(), serializer.errors
        
        updated_booking = serializer.save()
        
        # Check the booking was updated correctly
        assert updated_booking.id == booking.id
        assert str(updated_booking.start_time) == update_data['start_time']
        assert str(updated_booking.end_time) == update_data['end_time'] 