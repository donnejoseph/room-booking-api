from rest_framework import serializers
from .models import Room
from typing import Dict, Any
from django.utils import timezone
from datetime import datetime
from django.utils.dateparse import parse_date
from django.db import models
from bookings.models import Booking


class RoomSerializer(serializers.ModelSerializer):
    """
    Serializer for Room objects.
    """
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'floor', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate room data.
        
        Args:
            data: Data to validate
            
        Returns:
            Dict[str, Any]: Validated data
        """
        # Ensure floor and capacity are positive
        if data.get('floor', 0) <= 0:
            raise serializers.ValidationError({'floor': 'Floor must be a positive number.'})
        
        if data.get('capacity', 0) <= 0:
            raise serializers.ValidationError({'capacity': 'Capacity must be a positive number.'})
        
        return data


class RoomDetailSerializer(RoomSerializer):
    """
    Serializer for detailed Room information including availability.
    """
    is_available = serializers.SerializerMethodField()
    
    class Meta(RoomSerializer.Meta):
        fields = RoomSerializer.Meta.fields + ['is_available']
    
    def get_is_available(self, obj: Room) -> bool:
        """
        Get room availability for the specified date and time.
        
        Args:
            obj: Room object
            
        Returns:
            bool: True if the room is available, False otherwise
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'query_params'):
            return True
            
        date = request.query_params.get('date')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        
        if not all([date, start_time, end_time]):
            return True
        
        # Parse the date if it's a string
        if isinstance(date, str):
            try:
                parsed_date = parse_date(date)
                if parsed_date:
                    date = parsed_date
            except Exception:
                pass
        
        # Check if there are any overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=obj,
            date=date,
        ).filter(
            models.Q(start_time__lt=end_time, end_time__gt=start_time)
        )
        
        is_available = not overlapping_bookings.exists()
        return is_available 