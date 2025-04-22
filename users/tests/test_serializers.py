import pytest
from django.contrib.auth.models import User
from users.serializers import (
    UserSerializer, 
    UserProfileSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)
from rest_framework.exceptions import ValidationError


@pytest.mark.django_db
class TestUserSerializer:
    """Test suite for UserSerializer."""

    def test_user_serialization(self, user):
        """Test serializing a user."""
        serializer = UserSerializer(user)
        
        data = serializer.data
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert 'profile' in data
        assert 'is_staff' in data
        assert 'password' not in data  # Password should not be serialized
        
    def test_user_update(self, user):
        """Test updating a user via serializer."""
        data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'profile': {
                'department': 'IT',
                'phone_number': '+9876543210'
            }
        }
        
        serializer = UserSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()
        
        # Check user data was updated
        assert updated_user.username == 'updateduser'
        assert updated_user.email == 'updated@example.com'
        assert updated_user.first_name == 'Updated'
        assert updated_user.last_name == 'User'
        
        # Check profile data was updated
        assert updated_user.profile.department == 'IT'
        assert updated_user.profile.phone_number == '+9876543210'


@pytest.mark.django_db
class TestRegisterSerializer:
    """Test suite for RegisterSerializer."""

    def test_valid_registration(self):
        """Test valid user registration."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'department': 'Sales',
                'phone_number': '+1122334455'
            }
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('ComplexPass123!')  # Password should be hashed
        assert user.profile.department == 'Sales'
        
    def test_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ComplexPass123!',
            'password2': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        
    def test_duplicate_email(self):
        """Test registration with an email that already exists."""
        # Create a user with the email
        User.objects.create_user(
            username='existing',
            email='duplicate@example.com',
            password='existingpass'
        )
        
        # Try to register with the same email
        data = {
            'username': 'newuser',
            'email': 'duplicate@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
class TestChangePasswordSerializer:
    """Test suite for ChangePasswordSerializer."""

    def test_valid_password_change(self, user):
        """Test valid password change."""
        data = {
            'old_password': 'testpassword',  # From the user fixture
            'new_password': 'NewComplex123!',
            'new_password2': 'NewComplex123!'
        }
        
        serializer = ChangePasswordSerializer(data=data)
        assert serializer.is_valid()
        
    def test_password_mismatch(self):
        """Test password change with mismatched new passwords."""
        data = {
            'old_password': 'testpassword',
            'new_password': 'NewComplex123!',
            'new_password2': 'Different123!'
        }
        
        serializer = ChangePasswordSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors 