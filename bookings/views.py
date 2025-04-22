from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Booking
from .serializers import BookingSerializer
from core.permissions import IsOwnerOrAdmin
from django.db.models import QuerySet
from typing import Any


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for bookings.
    
    list: List all bookings (admin) or own bookings (regular user)
    retrieve: Get a specific booking (owner or admin)
    create: Create a new booking (authenticated users)
    update: Update a booking (owner or admin)
    partial_update: Partially update a booking (owner or admin)
    destroy: Delete a booking (owner or admin)
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'room']
    ordering_fields = ['date', 'start_time', 'end_time']
    ordering = ['date', 'start_time']
    
    def get_queryset(self) -> QuerySet:
        """
        Return all bookings for admin users or user's own bookings for regular users.
        """
        # Handle schema generation for Swagger/OpenAPI
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
            
        user = self.request.user
        
        # Admin can see all bookings
        if user.is_staff:
            return Booking.objects.all()
            
        # Regular users can only see their own bookings
        return Booking.objects.filter(user=user)
        
    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Create a new booking.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
    def perform_create(self, serializer: BookingSerializer) -> None:
        """
        Set the user to the current user when creating a booking.
        """
        serializer.save(user=self.request.user)
        
    def update(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Update a booking.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
        
    def destroy(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        """
        Delete a booking.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
