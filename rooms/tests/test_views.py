import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import time
from rest_framework import status
from rest_framework.test import APIClient
from rooms.models import Room


@pytest.mark.django_db
class TestRoomViewSet:
    """Test suite for RoomViewSet API endpoints."""

    def test_list_rooms(self, api_client, room, user):
        """Test listing all rooms."""
        # Authentication required
        api_client.force_authenticate(user=user)
        
        url = reverse('room-list')
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert response.data['results'][0]['id'] == room.id
        assert response.data['results'][0]['name'] == room.name
        
    def test_list_rooms_unauthenticated(self, api_client):
        """Test listing rooms when unauthenticated."""
        url = reverse('room-list')
        response = api_client.get(url)
        
        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_retrieve_room(self, api_client, room, user):
        """Test retrieving a specific room."""
        # Authentication required
        api_client.force_authenticate(user=user)
        
        url = reverse('room-detail', kwargs={'pk': room.id})
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == room.id
        assert response.data['name'] == room.name
        assert 'is_available' in response.data  # Detail serializer includes availability
        
    def test_create_room_as_admin(self, api_client, admin_user):
        """Test creating a room as admin user."""
        # Authenticate as admin
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('room-list')
        data = {
            'name': 'Admin Created Room',
            'capacity': 15,
            'floor': 3
        }
        
        response = api_client.post(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Admin Created Room'
        assert response.data['capacity'] == 15
        assert response.data['floor'] == 3
        
        # Check the room was created in the database
        assert Room.objects.filter(name='Admin Created Room').exists()
        
    def test_create_room_as_regular_user(self, api_client, user):
        """Test creating a room as a regular (non-admin) user."""
        # Authenticate as regular user
        api_client.force_authenticate(user=user)
        
        url = reverse('room-list')
        data = {
            'name': 'User Created Room',
            'capacity': 10,
            'floor': 2
        }
        
        response = api_client.post(url, data, format='json')
        
        # Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Check the room was not created
        assert not Room.objects.filter(name='User Created Room').exists()
        
    def test_update_room_as_admin(self, api_client, room, admin_user):
        """Test updating a room as admin user."""
        # Authenticate as admin
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('room-detail', kwargs={'pk': room.id})
        data = {
            'name': 'Updated Room Name',
            'capacity': 25,
            'floor': 4
        }
        
        response = api_client.put(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Room Name'
        assert response.data['capacity'] == 25
        assert response.data['floor'] == 4
        
        # Refresh room from database
        room.refresh_from_db()
        assert room.name == 'Updated Room Name'
        assert room.capacity == 25
        assert room.floor == 4
        
    def test_update_room_as_regular_user(self, api_client, room, user):
        """Test updating a room as a regular (non-admin) user."""
        # Authenticate as regular user
        api_client.force_authenticate(user=user)
        
        url = reverse('room-detail', kwargs={'pk': room.id})
        data = {
            'name': 'User Updated Room',
            'capacity': 30,
            'floor': 5
        }
        
        response = api_client.put(url, data, format='json')
        
        # Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Room should not be updated
        room.refresh_from_db()
        assert room.name != 'User Updated Room'
        
    def test_delete_room_as_admin(self, api_client, admin_user):
        """Test deleting a room as admin user."""
        # Create a room to delete
        room = Room.objects.create(name='Room To Delete', capacity=5, floor=1)
        
        # Authenticate as admin
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('room-detail', kwargs={'pk': room.id})
        response = api_client.delete(url)
        
        # Check response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check the room was deleted
        assert not Room.objects.filter(id=room.id).exists()
        
    def test_delete_room_as_regular_user(self, api_client, room, user):
        """Test deleting a room as a regular (non-admin) user."""
        # Authenticate as regular user
        api_client.force_authenticate(user=user)
        
        url = reverse('room-detail', kwargs={'pk': room.id})
        response = api_client.delete(url)
        
        # Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Room should not be deleted
        assert Room.objects.filter(id=room.id).exists()
        
    def test_filter_rooms_by_capacity(self, api_client, user):
        """Test filtering rooms by capacity."""
        # Create rooms with different capacities
        Room.objects.create(name='Small Room', capacity=5, floor=1)
        Room.objects.create(name='Medium Room', capacity=10, floor=1)
        Room.objects.create(name='Large Room', capacity=20, floor=1)
        
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Filter rooms with capacity >= 10
        url = reverse('room-list')
        response = api_client.get(url, {'capacity': 10})
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Should include only medium and large rooms
        rooms = response.data['results']
        assert len(rooms) == 2
        room_names = [room['name'] for room in rooms]
        assert 'Small Room' not in room_names
        assert 'Medium Room' in room_names
        assert 'Large Room' in room_names
        
    def test_filter_rooms_by_floor(self, api_client, user):
        """Test filtering rooms by floor."""
        # Create rooms on different floors
        Room.objects.create(name='First Floor Room', capacity=10, floor=1)
        Room.objects.create(name='Second Floor Room', capacity=10, floor=2)
        Room.objects.create(name='Third Floor Room', capacity=10, floor=3)
        
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Filter rooms on floor 2
        url = reverse('room-list')
        response = api_client.get(url, {'floor': 2})
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Should include only rooms on floor 2
        rooms = response.data['results']
        room_names = [room['name'] for room in rooms]
        assert 'First Floor Room' not in room_names
        assert 'Second Floor Room' in room_names
        assert 'Third Floor Room' not in room_names
        
    def test_filter_rooms_by_availability(self, api_client, room, user, booking):
        """Test filtering rooms by availability."""
        # Create additional rooms
        Room.objects.create(name='Available Room 1', capacity=10, floor=1)
        Room.objects.create(name='Available Room 2', capacity=15, floor=2)
        
        # room fixture has a booking from 10:00 to 11:00 today
        today = timezone.now().date()
        
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Filter rooms available from 10:00 to 11:00 today (when room fixture is booked)
        url = reverse('room-list')
        params = {
            'date': str(today),
            'start_time': '10:00:00',
            'end_time': '11:00:00'
        }
        
        response = api_client.get(url, params)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        
        # Should include all rooms except the one with a booking
        rooms = response.data['results']
        room_ids = [room['id'] for room in rooms]
        assert room.id not in room_ids  # Booked room should not be included
        assert len(rooms) >= 2  # Should include the available rooms 