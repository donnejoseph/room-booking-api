# Meeting Room Booking API

A Django REST API for booking meeting rooms in an office environment.

## Features

- User authentication with JWT tokens
- Room management (admin only for creation/modification)
- Booking management
- Room availability checking
- API documentation with Swagger/ReDoc

## Tech Stack

- Django 4.x
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Swagger/ReDoc for API documentation

## Requirements

- Python 3.8+
- PostgreSQL
- Docker (optional)

## Setup

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=booking_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1
```

### Local Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up the database:

```bash
python manage.py migrate
```

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## API Endpoints

### Authentication

- `POST /api/v1/auth/token/` - Obtain JWT token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `POST /api/v1/auth/register/` - Register a new user

### Users

- `GET /api/v1/users/profile/` - Get user profile
- `PUT/PATCH /api/v1/users/profile/` - Update user profile
- `POST /api/v1/users/change-password/` - Change password

### Rooms

- `GET /api/v1/rooms/` - List all rooms (with filtering options)
- `GET /api/v1/rooms/{id}/` - Get room details
- `POST /api/v1/rooms/` - Create a new room (admin only)
- `PUT/PATCH /api/v1/rooms/{id}/` - Update a room (admin only)
- `DELETE /api/v1/rooms/{id}/` - Delete a room (admin only)

### Bookings

- `GET /api/v1/bookings/` - List user's bookings (all bookings for admin)
- `GET /api/v1/bookings/{id}/` - Get booking details
- `POST /api/v1/bookings/` - Create a new booking
- `PUT/PATCH /api/v1/bookings/{id}/` - Update a booking
- `DELETE /api/v1/bookings/{id}/` - Delete a booking

## Filtering Options

### Rooms

- `floor` - Filter by floor number
- `capacity` - Filter by minimum capacity
- `date`, `start_time`, `end_time` - Filter by availability

### Bookings

- `date` - Filter by date
- `room` - Filter by room ID

## Running Tests

```bash
pytest
```

To run specific test categories:

```bash
# Run unit tests
pytest -m unit

# Run API tests
pytest -m api

# Run tests for a specific app
pytest -m rooms
```

## License

MIT 