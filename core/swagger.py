from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path

schema_info = openapi.Info(
    title="Meeting Room Booking API",
    default_version='v1',
    description="""
# Meeting Room Booking API Documentation

This API provides functionality for booking meeting rooms in an office.

## Features
- User authentication with JWT tokens
- Room management (admin only for creation/modification)
- Booking management
- Room availability checking

## Authentication
All API endpoints (except authentication endpoints) require a valid JWT token.
To authenticate, make a POST request to `/api/v1/auth/token/` with your username and password.
The response will include an access token and a refresh token.
Include the access token in the Authorization header of your requests using the Bearer scheme.

Example: `Authorization: Bearer <your_access_token>`

## Permissions
- Regular users can view rooms and manage their own bookings
- Admin users can create, update, and delete rooms, and view all bookings

## Endpoint Groups
- **Authentication**: User registration, token handling
- **Users**: User profile management
- **Rooms**: Room CRUD operations, filtering by availability
- **Bookings**: Booking CRUD operations
    """,
    terms_of_service="https://www.example.com/terms/",
    contact=openapi.Contact(email="contact@example.com"),
    license=openapi.License(name="BSD License"),
)

schema_view = get_schema_view(
    schema_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
) 