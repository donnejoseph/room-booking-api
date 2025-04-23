from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, time
from typing import Optional, Any, Dict

User = get_user_model()


class Booking(models.Model):
    """
    Model representing a room booking.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    room = models.ForeignKey(
        'rooms.Room', 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            ),
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['room', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self) -> str:
        return f"{self.room.name} - {self.date} {self.start_time} to {self.end_time} (by {self.user.username})"

    def clean(self) -> None:
        """
        Validate the booking:
        1. End time must be after start time
        2. Date must not be in the past
        3. Room must be available during the requested time slot
        4. User must not have other bookings that overlap with this one
        """
        # Check if date is in the past
        if self.date < timezone.now().date():
            raise ValidationError({
                'date': 'Booking date cannot be in the past.'
            })

        # Check if end time is after start time
        if self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': 'End time must be after start time.'
            })

        # Check room availability
        self._validate_room_availability()
        
        # Check user's other bookings
        self._validate_user_availability()

    def _validate_room_availability(self) -> None:
        """Check if the room is available during the requested time slot."""
        # Skip validation if this is an existing booking being updated
        if self.pk:
            overlapping_bookings = Booking.objects.filter(
                room=self.room,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)
        else:
            overlapping_bookings = Booking.objects.filter(
                room=self.room,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )

        if overlapping_bookings.exists():
            raise ValidationError({
                'non_field_errors': 'This room is already booked during the requested time slot.'
            })

    def _validate_user_availability(self) -> None:
        """Check if the user has other bookings that overlap with this one."""
        # Skip validation if this is an existing booking being updated
        if self.pk:
            overlapping_bookings = Booking.objects.filter(
                user=self.user,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk)
        else:
            overlapping_bookings = Booking.objects.filter(
                user=self.user,
                date=self.date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )

        if overlapping_bookings.exists():
            raise ValidationError({
                'non_field_errors': 'You already have another booking during this time slot.'
            })
            
    def save(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """Override save method to perform validation."""
        self.clean()
        super().save(*args, **kwargs)
