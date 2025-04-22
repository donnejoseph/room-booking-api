from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile
from typing import Dict, Any

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    class Meta:
        model = UserProfile
        fields = ['department', 'phone_number']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User objects.
    """
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'is_staff']
        read_only_fields = ['id', 'is_staff']
        ref_name = "UserProfileSerializer"
        
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        Update User and associated UserProfile.
        
        Args:
            instance: User instance
            validated_data: Validated data
            
        Returns:
            User: Updated user
        """
        profile_data = validated_data.pop('profile', {})
        
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update UserProfile fields
        if profile_data:
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            
            instance.profile.save()
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 
            'first_name', 'last_name', 'profile'
        ]
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate registration data.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict[str, Any]: Validated data
        """
        # Check if passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        
        # Check if email is unique
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'A user with this email already exists.'
            })
        
        return data
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new user.
        
        Args:
            validated_data: Validated data
            
        Returns:
            User: Created user
        """
        # Remove password2 and profile from validated data
        validated_data.pop('password2')
        profile_data = validated_data.pop('profile', {})
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Update profile if data provided
        if profile_data:
            for attr, value in profile_data.items():
                setattr(user.profile, attr, value)
            
            user.profile.save()
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate password change data.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict[str, Any]: Validated data
        """
        # Check if new passwords match
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'New passwords do not match.'
            })
        
        return data 