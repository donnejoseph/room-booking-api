import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rooms.models import Room
from bookings.models import Booking
from typing import Dict, Any

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.bookings
@pytest.mark.api
class TestBookingAPI:
    """Integration tests for Booking API endpoints."""

    @pytest.fixture
    def api_client(self):
        """Return an API client."""
        return APIClient()
        
    @pytest.fixture
    def user(self):
        """Create a regular user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
    @pytest.fixture
    def room1(self):
        """Create first test room."""
        return Room.objects.create(
            name="Meeting Room A",
            capacity=8,
            floor=1
        )
        
    @pytest.fixture
    def room2(self):
        """Create second test room."""
        return Room.objects.create(
            name="Conference Room B",
            capacity=20,
            floor=2
        )
        
    @pytest.fixture
    def today(self):
        """Return today's date."""
        return timezone.now().date()
        
    @pytest.fixture
    def tomorrow(self, today):
        """Return tomorrow's date."""
        return today + timedelta(days=1)
    
    def test_find_available_rooms(self, api_client, user, room1, room2, today):
        """Test finding available rooms for a specific time slot."""
        # Create a booking for room1 from 10:00 to 11:00
        Booking.objects.create(
            user=user,
            room=room1,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Request available rooms for the same time slot
        url = reverse('room-list')
        params = {
            'date': str(today),
            'start_time': '10:00:00',
            'end_time': '11:00:00'
        }
        
        response = api_client.get(url, params)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Only room2 should be available
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['id'] == room2.id
        
        # Check for a different time slot where both rooms should be available
        params = {
            'date': str(today),
            'start_time': '14:00:00',
            'end_time': '15:00:00'
        }
        
        response = api_client.get(url, params)
        
        # Check both rooms are available
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
    def test_create_and_cancel_booking_flow(self, api_client, user, room1, tomorrow):
        """Test the full flow of creating and then canceling a booking."""
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # 1. Create a booking
        create_url = reverse('booking-list')
        booking_data = {
            'room_id': room1.id,
            'date': str(tomorrow),
            'start_time': '09:00:00',
            'end_time': '10:00:00'
        }
        
        create_response = api_client.post(create_url, booking_data, format='json')
        
        # Check booking was created
        assert create_response.status_code == status.HTTP_201_CREATED
        booking_id = create_response.data['id']
        
        # 2. Verify the room is no longer available for that time slot
        rooms_url = reverse('room-list')
        availability_params = {
            'date': str(tomorrow),
            'start_time': '09:00:00',
            'end_time': '10:00:00'
        }
        
        rooms_response = api_client.get(rooms_url, availability_params)
        assert rooms_response.status_code == status.HTTP_200_OK
        assert len(rooms_response.data['results']) == 0  # No available rooms
        
        # 3. Cancel (delete) the booking
        delete_url = reverse('booking-detail', kwargs={'pk': booking_id})
        delete_response = api_client.delete(delete_url)
        
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 4. Verify the room is available again
        rooms_response = api_client.get(rooms_url, availability_params)
        assert rooms_response.status_code == status.HTTP_200_OK
        assert len(rooms_response.data['results']) == 1  # Room is available again
        assert rooms_response.data['results'][0]['id'] == room1.id
        
    def test_booking_time_conflict_resolution(self, api_client, user, room1, tomorrow):
        """Test booking conflicts and resolution."""
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # 1. Create an initial booking
        create_url = reverse('booking-list')
        initial_booking_data = {
            'room_id': room1.id,
            'date': str(tomorrow),
            'start_time': '13:00:00',
            'end_time': '14:00:00'
        }
        
        initial_response = api_client.post(create_url, initial_booking_data, format='json')
        assert initial_response.status_code == status.HTTP_201_CREATED
        
        # 2. Try to create a conflicting booking
        conflict_booking_data = {
            'room_id': room1.id,
            'date': str(tomorrow),
            'start_time': '13:30:00',  # Overlaps with 13:00-14:00
            'end_time': '14:30:00'
        }
        
        conflict_response = api_client.post(create_url, conflict_booking_data, format='json')
        assert conflict_response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in conflict_response.data
        
        # 3. Create a non-conflicting booking
        valid_booking_data = {
            'room_id': room1.id,
            'date': str(tomorrow),
            'start_time': '14:00:00',  # Starts right after the first booking ends
            'end_time': '15:00:00'
        }
        
        valid_response = api_client.post(create_url, valid_booking_data, format='json')
        assert valid_response.status_code == status.HTTP_201_CREATED
        
    def test_booking_statistics(self, api_client, user, room1, room2, today, tomorrow):
        """Test retrieving user's booking statistics."""
        # Create a series of bookings
        Booking.objects.create(
            user=user,
            room=room1,
            date=today,
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        
        Booking.objects.create(
            user=user,
            room=room2,
            date=today,
            start_time=time(14, 0),
            end_time=time(15, 0)
        )
        
        Booking.objects.create(
            user=user,
            room=room1,
            date=tomorrow,
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Get user's bookings
        url = reverse('booking-list')
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        
        # Filter by today's date
        response = api_client.get(f"{url}?date={today}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Filter by room1
        response = api_client.get(f"{url}?room={room1.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
    def test_user_cannot_double_book(self, api_client, user, room1, room2, tomorrow):
        """Test that a user cannot book two rooms at the same time."""
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Create first booking
        create_url = reverse('booking-list')
        first_booking_data = {
            'room_id': room1.id,
            'date': str(tomorrow),
            'start_time': '15:00:00',
            'end_time': '16:00:00'
        }
        
        first_response = api_client.post(create_url, first_booking_data, format='json')
        assert first_response.status_code == status.HTTP_201_CREATED
        
        # Try to book a different room at the same time
        second_booking_data = {
            'room_id': room2.id,
            'date': str(tomorrow),
            'start_time': '15:00:00',
            'end_time': '16:00:00'
        }
        
        second_response = api_client.post(create_url, second_booking_data, format='json')
        assert second_response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in second_response.data 