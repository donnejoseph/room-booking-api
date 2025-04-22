import pytest
from django.contrib.auth.models import User
from users.models import UserProfile
from django.db import IntegrityError


@pytest.mark.django_db
class TestUserProfileModel:
    """Test suite for the UserProfile model."""

    def test_profile_creation(self, user):
        """Test that a UserProfile is automatically created when a User is created."""
        # The profile should have been created by the signal
        assert UserProfile.objects.filter(user=user).exists()
        
        # Check that profile is accessible via related name
        assert user.profile is not None
        assert isinstance(user.profile, UserProfile)
        
    def test_profile_str_representation(self, user):
        """Test the string representation of UserProfile."""
        profile = user.profile
        assert str(profile) == f"{user.username}'s Profile"
        
    def test_profile_fields(self):
        """Test creating a profile with all fields."""
        user = User.objects.create_user(
            username="fielduser",
            email="fields@example.com",
            password="password123"
        )
        
        # Update profile fields
        profile = user.profile
        profile.department = "Engineering"
        profile.phone_number = "+1234567890"
        profile.save()
        
        # Refresh from db and check
        profile.refresh_from_db()
        assert profile.department == "Engineering"
        assert profile.phone_number == "+1234567890"
        
    def test_profile_user_deletion(self):
        """Test that UserProfile is deleted when User is deleted (cascade)."""
        user = User.objects.create_user(
            username="tempuser",
            email="temp@example.com",
            password="temppass123"
        )
        
        profile_id = user.profile.id
        assert UserProfile.objects.filter(id=profile_id).exists()
        
        # Delete the user
        user.delete()
        
        # Profile should be deleted due to CASCADE
        assert not UserProfile.objects.filter(id=profile_id).exists()
        
    def test_profile_unique_constraint(self):
        """Test that a user can have only one profile."""
        user = User.objects.create_user(
            username="uniqueuser",
            email="unique@example.com",
            password="uniquepass"
        )
        
        # Try to create another profile for the same user
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user) 