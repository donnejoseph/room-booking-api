from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Room
from .serializers import RoomSerializer, RoomDetailSerializer
from .filters import RoomFilter
from core.permissions import IsAdminUserOrReadOnly
from django.db.models import QuerySet
from typing import Type, Any


class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for rooms.
    
    list: List all rooms (all users)
    retrieve: Get a specific room (all users)
    create: Create a new room (admin only)
    update: Update a room (admin only)
    partial_update: Partially update a room (admin only)
    destroy: Delete a room (admin only)
    """
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RoomFilter
    search_fields = ['name']
    ordering_fields = ['name', 'floor', 'capacity']
    
    def get_serializer_class(self) -> Type[RoomSerializer]:
        """
        Return the appropriate serializer class for the request.
        """
        if self.action == 'retrieve':
            return RoomDetailSerializer
        return RoomSerializer
    
    def get_queryset(self) -> QuerySet:
        """
        Optionally filter rooms by date, time, floor and capacity.
        """
        queryset = Room.objects.all()
        
        # Get query params
        date = self.request.query_params.get('date')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        floor = self.request.query_params.get('floor')
        capacity = self.request.query_params.get('capacity')
        
        # Filter by floor
        if floor:
            queryset = queryset.filter(floor=floor)
            
        # Filter by capacity
        if capacity:
            queryset = queryset.filter(capacity__gte=capacity)
            
        # Filter by availability
        if all([date, start_time, end_time]):
            available_rooms = []
            for room in queryset:
                if room.is_available(date, start_time, end_time):
                    available_rooms.append(room.id)
            
            queryset = queryset.filter(id__in=available_rooms)
        
        return queryset
