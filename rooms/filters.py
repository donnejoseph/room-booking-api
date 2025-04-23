import django_filters
from .models import Room
from django.db.models import Q
from typing import Any, Dict


class RoomFilter(django_filters.FilterSet):
    """
    Filter for Room model.
    
    Allows filtering by:
    - floor (exact)
    - capacity (greater than or equal)
    - date, start_time, end_time (for availability)
    """
    floor = django_filters.NumberFilter(field_name='floor')
    capacity = django_filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    date = django_filters.DateFilter(method='filter_availability')
    start_time = django_filters.TimeFilter(method='filter_ignored')
    end_time = django_filters.TimeFilter(method='filter_ignored')
    
    class Meta:
        model = Room
        fields = ['floor', 'capacity', 'date', 'start_time', 'end_time']
    
    def filter_ignored(self, queryset, name, value) -> Any:
        """
        Placeholder filter method that doesn't filter.
        These parameters are actually used in filter_availability.
        
        Args:
            queryset: QuerySet to filter
            name: Name of the filter field
            value: Filter value
            
        Returns:
            QuerySet: Unfiltered queryset
        """
        return queryset
        
    def filter_availability(self, queryset, name, value) -> Any:
        """
        Filter rooms by availability.
        
        Args:
            queryset: QuerySet to filter
            name: Name of the filter field
            value: Filter value (date)
            
        Returns:
            QuerySet: Filtered queryset
        """
        # Get start_time and end_time from filters
        start_time = self.data.get('start_time')
        end_time = self.data.get('end_time')
        
        # If any parameter is missing, return all rooms
        if not all([value, start_time, end_time]):
            return queryset
            
        # Check availability for each room
        available_rooms = []
        for room in queryset:
            if room.is_available(value, start_time, end_time):
                available_rooms.append(room.id)
                
        return queryset.filter(id__in=available_rooms) 