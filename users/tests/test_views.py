import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserProfileView:
    """Test suite for UserProfileView API endpoint."""

    def test_get_profile_authenticated(self, api_client, user):
        """Test retrieving user profile when authenticated."""
        # Authenticate the user
        api_client.force_authenticate(user=user)
        
        # Get the profile
        url = reverse('user-profile')
        response = api_client.get(url)
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email
        assert 'profile' in response.data
        
    def test_get_profile_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot access profile."""
        url = reverse('user-profile')
        response = api_client.get(url)
        
        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_update_profile(self, api_client, user):
        """Test updating user profile."""
        # Authenticate the user
        api_client.force_authenticate(user=user)
        
        # Update data
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'profile': {
                'department': 'Research',
                'phone_number': '+1122334455'
            }
        }
        
        # Update the profile
        url = reverse('user-profile')
        response = api_client.patch(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
        assert response.data['profile']['department'] == 'Research'
        assert response.data['profile']['phone_number'] == '+1122334455'
        
        # Refresh user from database and check
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.profile.department == 'Research'


@pytest.mark.django_db
class TestRegisterView:
    """Test suite for RegisterView API endpoint."""

    def test_register_user(self, api_client):
        """Test registering a new user."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'department': 'Marketing',
                'phone_number': '+9988776655'
            }
        }
        
        response = api_client.post(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        
        # Check user was created
        assert User.objects.filter(username='newuser').exists()
        user = User.objects.get(username='newuser')
        assert user.email == 'new@example.com'
        assert user.first_name == 'New'
        assert user.profile.department == 'Marketing'
        
    def test_register_with_invalid_data(self, api_client):
        """Test registration with invalid data."""
        url = reverse('register')
        
        # Missing required fields
        data = {
            'username': 'newuser',
            # Missing password fields
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Password mismatch
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ComplexPass123!',
            'password2': 'Different123!'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


@pytest.mark.django_db
class TestChangePasswordView:
    """Test suite for ChangePasswordView API endpoint."""

    def test_change_password_success(self, api_client, user):
        """Test successfully changing a password."""
        # Authenticate the user
        api_client.force_authenticate(user=user)
        
        url = reverse('change-password')
        data = {
            'old_password': 'testpassword',  # From user fixture
            'new_password': 'NewSecure123!',
            'new_password2': 'NewSecure123!'
        }
        
        response = api_client.put(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Refresh user from DB and check password was changed
        user.refresh_from_db()
        assert user.check_password('NewSecure123!')
        
    def test_change_password_wrong_old_password(self, api_client, user):
        """Test that providing wrong old password fails."""
        # Authenticate the user
        api_client.force_authenticate(user=user)
        
        url = reverse('change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewSecure123!',
            'new_password2': 'NewSecure123!'
        }
        
        response = api_client.put(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in response.data
        
        # Password should not be changed
        user.refresh_from_db()
        assert not user.check_password('NewSecure123!')
        assert user.check_password('testpassword')
        
    def test_change_password_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot change password."""
        url = reverse('change-password')
        data = {
            'old_password': 'testpassword',
            'new_password': 'NewSecure123!',
            'new_password2': 'NewSecure123!'
        }
        
        response = api_client.put(url, data, format='json')
        
        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestJWTAuthentication:
    """Test suite for JWT authentication endpoints."""

    def test_obtain_token(self, api_client, user):
        """Test obtaining a JWT token."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',  # From user fixture
            'password': 'testpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        
    def test_refresh_token(self, api_client, user):
        """Test refreshing a JWT token."""
        # First, obtain a token
        obtain_url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        response = api_client.post(obtain_url, data, format='json')
        refresh_token = response.data['refresh']
        
        # Now try to refresh the token
        refresh_url = reverse('token_refresh')
        data = {
            'refresh': refresh_token
        }
        
        response = api_client.post(refresh_url, data, format='json')
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        
    def test_invalid_credentials(self, api_client):
        """Test that invalid credentials don't get a token."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        
        response = api_client.post(url, data, format='json')
        
        # Check response - should be unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 