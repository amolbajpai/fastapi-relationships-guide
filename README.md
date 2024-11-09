Here's a detailed `README.md` for your FastAPI project demonstrating a one-to-one relationship.

# FastAPI One-to-One Relationship Demo

This repository demonstrates a **one-to-one relationship** in FastAPI using SQLAlchemy. It provides a simple API for managing `User` and `Profile` entities with a one-to-one relationship, where each `User` has a single associated `Profile`.

## Project Structure

This demo API includes the following components:

- **FastAPI**: Used to create the API endpoints.
- **SQLAlchemy**: Manages the database models and relationships.
- **SQLite**: The database used for this demo.

## Table of Contents

- [Installation](#installation)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Project Details](#project-details)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/amolbajpai/fastapi-relationships-guide.git
   cd fastapi-relationships-guide
   ```

2. Install dependencies:
   ```bash
   pip install fastapi sqlalchemy pydantic uvicorn
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

The app will start at `http://127.0.0.1:8000`.

## Database Models

### User Model

The `User` model represents a user and includes:
- **id**: Primary key (integer).
- **name**: Name of the user (string).
- **profile**: One-to-one relationship to the `Profile` model.

### Profile Model

The `Profile` model represents a user's profile and includes:
- **id**: Primary key (integer).
- **bio**: Short bio of the user (string).
- **user_id**: Foreign key referencing the `User` model's ID.

A unique constraint is applied to `user_id` to enforce the one-to-one relationship.

### Pydantic Models

Pydantic models define the data structure for API requests and responses:
- **UserCreate**: Schema for creating a new user with a profile.
- **UserResponse**: Schema for returning user data, including profile bio.
- **ProfileCreate**: Schema for creating a profile for an existing user.
- **ProfileResponse**: Schema for returning profile data.

## API Endpoints

### Create a New User with Profile

**Endpoint**: `POST /users/`  
**Description**: Creates a new user with an associated profile.  
**Request Body**:  
```json
{
  "name": "User Name",
  "bio": "Short bio"
}
```
**Response**: Returns the created user's data along with their profile bio.

### Get All Users with Profiles

**Endpoint**: `GET /users`  
**Description**: Retrieves all users and their associated profile bios.  
**Response**: List of all users and their profile information.

### Get User by ID with Profile

**Endpoint**: `GET /users/{user_id}`  
**Description**: Retrieves a specific user and their profile by user ID.  
**Response**: Returns user details and profile bio.

### Update User and Profile by User ID

**Endpoint**: `PUT /users/{user_id}`  
**Description**: Updates a user's name and profile bio.  
**Request Body**:  
```json
{
  "name": "Updated Name",
  "bio": "Updated bio"
}
```
**Response**: Returns updated user and profile information.

### Delete a User

**Endpoint**: `DELETE /users/{user_id}`  
**Description**: Deletes a user and their associated profile.  
**Response**: Confirms successful deletion.

### Create a New Profile for an Existing User

**Endpoint**: `POST /profiles/`  
**Description**: Creates a profile for an existing user by `user_id`.  
**Request Body**:  
```json
{
  "bio": "User bio",
  "user_id": 1
}
```
**Response**: Returns the created profile information.

### Get Profile by ID

**Endpoint**: `GET /profiles/{profile_id}`  
**Description**: Retrieves a specific profile by profile ID.  
**Response**: Returns profile information.

### Get All Profiles

**Endpoint**: `GET /profiles`  
**Description**: Retrieves all profiles.  
**Response**: List of all profiles and their details.

## Usage

### Creating a User with Profile

To create a user and their profile in one go:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "John Doe",
    "bio": "A software developer"
  }'
```

### Retrieving All Users

To retrieve all users with their profiles:
```bash
curl -X 'GET' 'http://127.0.0.1:8000/users' -H 'accept: application/json'
```

### Updating a User's Profile

To update a user's profile:
```bash
curl -X 'PUT' \
  'http://127.0.0.1:8000/users/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Jane Doe",
    "bio": "An updated bio"
  }'
```

### Deleting a User

To delete a user:
```bash
curl -X 'DELETE' 'http://127.0.0.1:8000/users/1' -H 'accept: application/json'
```

## Project Details

- **Language**: Python
- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy

This example provides a fundamental introduction to managing one-to-one relationships in a FastAPI application using SQLAlchemy.
```