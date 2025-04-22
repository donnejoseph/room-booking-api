from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from .models import Booking
from rooms.models import Room
from rooms.serializers import RoomSerializer
from django.contrib.auth import get_user_model
from typing import Dict, Any

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User objects in the context of bookings.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name = "BookingUserSerializer"


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking objects.
    """
    user = UserSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), 
        source='room',
        write_only=True
    )
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'room', 'room_id', 'date', 
            'start_time', 'end_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate booking data.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict[str, Any]: Validated data
        """
        # Check if date is in the past
        if data.get('date') and data['date'] < timezone.now().date():
            raise serializers.ValidationError({'date': 'Booking date cannot be in the past.'})
        
        # Check if end time is after start time
        if data.get('start_time') and data.get('end_time') and data['end_time'] <= data['start_time']:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
        
        # Check room availability
        room = data.get('room')
        date = data.get('date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if all([room, date, start_time, end_time]):
            # For existing booking, exclude the current instance
            instance = self.instance
            
            # Check if room is available
            if not self._is_room_available(room, date, start_time, end_time, instance):
                raise serializers.ValidationError({
                    'non_field_errors': 'This room is already booked during the requested time slot.'
                })
                
            # Check if user has other bookings during this time
            user = self.context['request'].user
            if not self._is_user_available(user, date, start_time, end_time, instance):
                raise serializers.ValidationError({
                    'non_field_errors': 'You already have another booking during this time slot.'
                })
        
        return data
    
    def _is_room_available(self, room: Room, date: Any, start_time: Any, 
                          end_time: Any, instance: Booking = None) -> bool:
        """
        Check if the room is available during the requested time slot.
        
        Args:
            room: Room object
            date: Booking date
            start_time: Start time
            end_time: End time
            instance: Current booking instance if updating
            
        Returns:
            bool: True if room is available, False otherwise
        """
        # Query for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=room,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        # If updating, exclude the current instance
        if instance:
            overlapping_bookings = overlapping_bookings.exclude(pk=instance.pk)
            
        return not overlapping_bookings.exists()
    
    def _is_user_available(self, user: User, date: Any, start_time: Any, 
                          end_time: Any, instance: Booking = None) -> bool:
        """
        Check if the user has other bookings that overlap with this one.
        
        Args:
            user: User object
            date: Booking date
            start_time: Start time
            end_time: End time
            instance: Current booking instance if updating
            
        Returns:
            bool: True if user is available, False otherwise
        """
        # Query for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            user=user,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        # If updating, exclude the current instance
        if instance:
            overlapping_bookings = overlapping_bookings.exclude(pk=instance.pk)
            
        return not overlapping_bookings.exists()
        
    def create(self, validated_data: Dict[str, Any]) -> Booking:
        """
        Create a new booking.
        
        Args:
            validated_data: Validated data
            
        Returns:
            Booking: Created booking
        """
        with transaction.atomic():
            # Set the user to the current user
            validated_data['user'] = self.context['request'].user
            
            # Create the booking
            booking = Booking.objects.create(**validated_data)
            
            return booking
            
    def update(self, instance: Booking, validated_data: Dict[str, Any]) -> Booking:
        """
        Update an existing booking.
        
        Args:
            instance: Booking instance
            validated_data: Validated data
            
        Returns:
            Booking: Updated booking
        """
        with transaction.atomic():
            # Update the fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
                
            # Save the instance
            instance.save()
            
            return instance 