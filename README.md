# Meeting Room Booking System

REST API for office meeting room booking system. Developed using Django and Django REST Framework.

## Project Description

The system allows users to:
- View available meeting rooms with filtering options
- Book free time slots
- Manage their bookings
- Administrators can manage rooms and view all bookings

### Core Entities

- **User**: Authenticated system user with profile
- **Room**: Meeting room with name, capacity, and floor
- **Booking**: Room reservation for a specific date and time

## Technologies

- Python 3.10+
- Django 5.2
- Django REST Framework
- PostgreSQL
- JWT authentication (Simple JWT)
- Swagger/ReDoc for API documentation
- Docker and docker-compose
- Pytest for testing

## Project Setup

### Using Docker (recommended)

1. Clone the repository:
```bash
git clone https://github.com/your-username/room-booking-api.git
cd room-booking-api
```

2. Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-should-be-very-long-and-secure
DB_NAME=booking_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

3. Start the containers:
```bash
docker-compose up -d
```

4. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

The application will be available at: http://localhost:8000/

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/room-booking-api.git
cd room-booking-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root (see example above, but change DB_HOST to localhost)

5. Set up PostgreSQL database and run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## API Documentation

After starting the server, API documentation is available at the following links:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Main API Endpoints

### Authentication
- `POST /api/v1/auth/token/` - Obtain JWT token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `POST /api/v1/auth/register/` - Register a new user

### User Profile
- `GET /api/v1/users/profile/` - Get user profile
- `PUT/PATCH /api/v1/users/profile/` - Update profile
- `POST /api/v1/users/change-password/` - Change password

### Meeting Rooms
- `GET /api/v1/rooms/` - List all rooms with filtering options
- `GET /api/v1/rooms/{id}/` - Get details of a specific room
- `POST /api/v1/rooms/` - Create a new room (admin only)
- `PUT/PATCH /api/v1/rooms/{id}/` - Update a room (admin only)
- `DELETE /api/v1/rooms/{id}/` - Delete a room (admin only)

### Bookings
- `GET /api/v1/bookings/` - List user's bookings (all bookings for admin)
- `GET /api/v1/bookings/{id}/` - Get details of a specific booking
- `POST /api/v1/bookings/` - Create a new booking
- `PUT/PATCH /api/v1/bookings/{id}/` - Update a booking
- `DELETE /api/v1/bookings/{id}/` - Delete a booking

## Filtering Parameters

### Rooms
- `floor` - Filter by floor
- `capacity` - Filter by minimum capacity
- `date`, `start_time`, `end_time` - Filter by availability at specified time

### Bookings
- `date` - Filter by date
- `room` - Filter by room ID

## Tests

The project has 98% test coverage, including unit tests and API tests.

Run all tests:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov=users --cov=rooms --cov=bookings --cov=core
```

Generate HTML coverage report:
```bash
coverage html
```

## API Usage Examples

### Getting a token
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### Getting a list of available rooms
```bash
curl -X GET "http://localhost:8000/api/v1/rooms/?date=2023-05-01&start_time=10:00:00&end_time=11:00:00&capacity=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Creating a booking
```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"room_id": 1, "date": "2023-05-01", "start_time": "10:00:00", "end_time": "11:00:00"}'
```

## Project Structure

- `core/` - Core project settings
- `users/` - User management and authentication
- `rooms/` - Meeting room management
- `bookings/` - Booking management

## Implementation Features

- Validation for overlapping bookings by time
- Room availability check for requested time slot
- Prohibition on booking more than one room by a user at the same time
- Optimized queries using indexes for high performance
- Separation of access rights between regular users and administrators 