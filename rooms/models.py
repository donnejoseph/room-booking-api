from django.db import models
from django.core.validators import MinValueValidator
from typing import Optional


class Room(models.Model):
    """
    Model representing a meeting room in the office.
    """
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    floor = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['floor', 'name']
        verbose_name = 'Meeting Room'
        verbose_name_plural = 'Meeting Rooms'
        indexes = [
            models.Index(fields=['floor']),
            models.Index(fields=['capacity']),
        ]

    def __str__(self) -> str:
        return f"{self.name} (Floor {self.floor}, Capacity: {self.capacity})"
    
    def is_available(self, date, start_time, end_time) -> bool:
        """
        Check if the room is available for the specified time slot.
        
        Args:
            date: The date to check availability for
            start_time: The start time of the slot
            end_time: The end time of the slot
            
        Returns:
            bool: True if the room is available, False otherwise
        """
        from bookings.models import Booking
        
        # Check for any overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=self,
            date=date,
        ).filter(
            # Case 1: Start time of new booking is during an existing booking
            # Case 2: End time of new booking is during an existing booking
            # Case 3: New booking completely contains an existing booking
            models.Q(start_time__lt=end_time, end_time__gt=start_time)
        )
        
        return not overlapping_bookings.exists()
