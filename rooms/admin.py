from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'floor', 'created_at', 'updated_at')
    list_filter = ('floor', 'capacity')
    search_fields = ('name', 'floor')
    ordering = ('floor', 'name')
