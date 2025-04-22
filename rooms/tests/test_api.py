import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rooms.models import Room
from typing import Dict, Any

User = get_user_model()


@pytest.mark.rooms
@pytest.mark.api
class TestRoomAPI:
    """Tests for Room API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Return an API client."""
        return APIClient()
        
    @pytest.fixture
    def user(self):
        """Create a regular user."""
        return User.objects.create_user(
            username="user",
            email="user@example.com",
            password="password"
        )
        
    @pytest.fixture
    def admin_user(self):
        """Create an admin user."""
        return User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password",
            is_staff=True
        )
        
    @pytest.fixture
    def room_data(self) -> Dict[str, Any]:
        """Return test room data."""
        return {
            'name': 'Test Room',
            'capacity': 10,
            'floor': 2
        }
        
    @pytest.fixture
    def room(self, room_data):
        """Create a test room."""
        return Room.objects.create(**room_data)
    
    def test_get_room_list_unauthenticated(self, api_client):
        """Test getting room list as unauthenticated user."""
        url = reverse('room-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_get_room_list_authenticated(self, api_client, user, room):
        """Test getting room list as authenticated user."""
        api_client.force_authenticate(user=user)
        url = reverse('room-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == room.name
        
    def test_get_room_detail(self, api_client, user, room):
        """Test getting room detail."""
        api_client.force_authenticate(user=user)
        url = reverse('room-detail', args=[room.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == room.name
        assert response.data['capacity'] == room.capacity
        assert response.data['floor'] == room.floor
        assert 'is_available' in response.data
        
    def test_create_room_as_regular_user(self, api_client, user, room_data):
        """Test creating room as regular user (should fail)."""
        api_client.force_authenticate(user=user)
        url = reverse('room-list')
        response = api_client.post(url, room_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Room.objects.count() == 0
        
    def test_create_room_as_admin(self, api_client, admin_user, room_data):
        """Test creating room as admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('room-list')
        response = api_client.post(url, room_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Room.objects.count() == 1
        room = Room.objects.first()
        assert room.name == room_data['name']
        
    def test_update_room_as_regular_user(self, api_client, user, room):
        """Test updating room as regular user (should fail)."""
        api_client.force_authenticate(user=user)
        url = reverse('room-detail', args=[room.id])
        update_data = {'name': 'Updated Room'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        room.refresh_from_db()
        assert room.name != 'Updated Room'
        
    def test_update_room_as_admin(self, api_client, admin_user, room):
        """Test updating room as admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('room-detail', args=[room.id])
        update_data = {'name': 'Updated Room'}
        response = api_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        room.refresh_from_db()
        assert room.name == 'Updated Room'
        
    def test_delete_room_as_regular_user(self, api_client, user, room):
        """Test deleting room as regular user (should fail)."""
        api_client.force_authenticate(user=user)
        url = reverse('room-detail', args=[room.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Room.objects.count() == 1
        
    def test_delete_room_as_admin(self, api_client, admin_user, room):
        """Test deleting room as admin."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('room-detail', args=[room.id])
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Room.objects.count() == 0
        
    def test_filter_rooms_by_floor(self, api_client, user):
        """Test filtering rooms by floor."""
        Room.objects.create(name="Room 1", capacity=10, floor=1)
        Room.objects.create(name="Room 2", capacity=15, floor=2)
        Room.objects.create(name="Room 3", capacity=20, floor=2)
        
        api_client.force_authenticate(user=user)
        url = reverse('room-list')
        response = api_client.get(f"{url}?floor=2")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
    def test_filter_rooms_by_capacity(self, api_client, user):
        """Test filtering rooms by capacity."""
        Room.objects.create(name="Room 1", capacity=10, floor=1)
        Room.objects.create(name="Room 2", capacity=15, floor=2)
        Room.objects.create(name="Room 3", capacity=20, floor=2)
        
        api_client.force_authenticate(user=user)
        url = reverse('room-list')
        response = api_client.get(f"{url}?capacity=15")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Room 2 and Room 3 