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
class TestBookingViewSet:
    """Test suite for BookingViewSet API endpoints."""

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
    def another_user(self):
        """Create another regular user."""
        return User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="anotherpassword"
        )
        
    @pytest.fixture
    def admin_user(self):
        """Create an admin user."""
        return User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword",
            is_staff=True
        )
        
    @pytest.fixture
    def room(self):
        """Create a test room."""
        return Room.objects.create(
            name="Test Room",
            capacity=10,
            floor=2
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
    def other_user_booking(self, room, another_user):
        """Create a booking for another user."""
        today = timezone.now().date()
        return Booking.objects.create(
            user=another_user,
            room=room,
            date=today,
            start_time=time(13, 0),
            end_time=time(14, 0)
        )
        
    @pytest.fixture
    def booking_data(self, room) -> Dict[str, Any]:
        """Return valid booking data."""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        return {
            'room_id': room.id,
            'date': str(tomorrow),
            'start_time': '15:00:00',
            'end_time': '16:00:00'
        }
        
    def test_list_bookings_unauthenticated(self, api_client):
        """Test listing bookings when unauthenticated."""
        url = reverse('booking-list')
        response = api_client.get(url)
        
        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_list_bookings_as_user(self, api_client, user, booking, other_user_booking):
        """Test listing bookings as a regular user (should see only own bookings)."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-list')
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Should only see own bookings
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == booking.id
        
    def test_list_bookings_as_admin(self, api_client, admin_user, booking, other_user_booking):
        """Test listing bookings as admin (should see all bookings)."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('booking-list')
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Should see all bookings
        assert len(response.data['results']) == 2
        
    def test_retrieve_own_booking(self, api_client, user, booking):
        """Test retrieving own booking."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id
        assert response.data['date'] == str(booking.date)
        assert response.data['start_time'] == str(booking.start_time)
        assert response.data['end_time'] == str(booking.end_time)
        
    def test_retrieve_other_user_booking(self, api_client, user, other_user_booking):
        """Test retrieving another user's booking (should fail)."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-detail', kwargs={'pk': other_user_booking.id})
        response = api_client.get(url)
        
        # Should return 404 Not Found (to not leak information)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_retrieve_booking_as_admin(self, api_client, admin_user, booking):
        """Test retrieving any booking as admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id
        
    def test_create_booking(self, api_client, user, booking_data):
        """Test creating a booking."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-list')
        response = api_client.post(url, booking_data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == booking_data['date']
        assert response.data['start_time'] == booking_data['start_time']
        assert response.data['end_time'] == booking_data['end_time']
        assert response.data['user']['username'] == user.username
        
        # Check the booking was created in the database
        assert Booking.objects.filter(
            date=booking_data['date'],
            start_time=booking_data['start_time']
        ).exists()
        
    def test_create_booking_with_conflict(self, api_client, user, booking):
        """Test creating a booking that conflicts with an existing one."""
        conflict_data = {
            'room_id': booking.room.id,
            'date': str(booking.date),
            'start_time': '10:30:00',  # Overlaps with 10:00-11:00
            'end_time': '11:30:00'
        }
        
        api_client.force_authenticate(user=user)
        url = reverse('booking-list')
        response = api_client.post(url, conflict_data, format='json')
        
        # Should return 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data
        
    def test_update_own_booking(self, api_client, user, booking):
        """Test updating own booking."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        
        # Update to a different time
        update_data = {
            'start_time': '14:00:00',
            'end_time': '15:00:00'
        }
        
        response = api_client.patch(url, update_data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['start_time'] == update_data['start_time']
        assert response.data['end_time'] == update_data['end_time']
        
        # Check the booking was updated in the database
        booking.refresh_from_db()
        assert str(booking.start_time) == update_data['start_time']
        assert str(booking.end_time) == update_data['end_time']
        
    def test_update_other_user_booking(self, api_client, user, other_user_booking):
        """Test updating another user's booking (should fail)."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-detail', kwargs={'pk': other_user_booking.id})
        
        update_data = {
            'start_time': '15:00:00',
            'end_time': '16:00:00'
        }
        
        response = api_client.patch(url, update_data, format='json')
        
        # Should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Booking should not be updated
        other_user_booking.refresh_from_db()
        assert str(other_user_booking.start_time) != update_data['start_time']
        
    def test_update_booking_as_admin(self, api_client, admin_user, booking):
        """Test updating any booking as admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        
        update_data = {
            'start_time': '16:00:00',
            'end_time': '17:00:00'
        }
        
        response = api_client.patch(url, update_data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Check the booking was updated
        booking.refresh_from_db()
        assert str(booking.start_time) == update_data['start_time']
        
    def test_delete_own_booking(self, api_client, user, booking):
        """Test deleting own booking."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = api_client.delete(url)
        
        # Check response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check the booking was deleted
        assert not Booking.objects.filter(id=booking.id).exists()
        
    def test_delete_other_user_booking(self, api_client, user, other_user_booking):
        """Test deleting another user's booking (should fail)."""
        api_client.force_authenticate(user=user)
        url = reverse('booking-detail', kwargs={'pk': other_user_booking.id})
        response = api_client.delete(url)
        
        # Should return 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Booking should not be deleted
        assert Booking.objects.filter(id=other_user_booking.id).exists()
        
    def test_delete_booking_as_admin(self, api_client, admin_user, booking):
        """Test deleting any booking as admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = api_client.delete(url)
        
        # Check response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check the booking was deleted
        assert not Booking.objects.filter(id=booking.id).exists()
        
    def test_filter_bookings_by_date(self, api_client, user):
        """Test filtering bookings by date."""
        # Create bookings on different dates
        room = Room.objects.create(name="Filter Room", capacity=10, floor=1)
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        Booking.objects.create(
            user=user,
            room=room,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        Booking.objects.create(
            user=user,
            room=room,
            date=tomorrow,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        # Filter by today
        api_client.force_authenticate(user=user)
        url = reverse('booking-list')
        response = api_client.get(f"{url}?date={today}")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['date'] == str(today)
        
    def test_filter_bookings_by_room(self, api_client, user):
        """Test filtering bookings by room."""
        # Create bookings for different rooms
        room1 = Room.objects.create(name="Room 1", capacity=10, floor=1)
        room2 = Room.objects.create(name="Room 2", capacity=15, floor=2)
        today = timezone.now().date()
        
        booking1 = Booking.objects.create(
            user=user,
            room=room1,
            date=today,
            start_time=time(10, 0),
            end_time=time(11, 0)
        )
        
        Booking.objects.create(
            user=user,
            room=room2,
            date=today,
            start_time=time(13, 0),
            end_time=time(14, 0)
        )
        
        # Filter by room1
        api_client.force_authenticate(user=user)
        url = reverse('booking-list')
        response = api_client.get(f"{url}?room={room1.id}")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == booking1.id 