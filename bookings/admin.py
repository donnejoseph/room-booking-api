from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'date', 'start_time', 'end_time', 'created_at')
    list_filter = ('date', 'room', 'user')
    search_fields = ('user__username', 'room__name', 'date')
    ordering = ('date', 'start_time')
    date_hierarchy = 'date'
