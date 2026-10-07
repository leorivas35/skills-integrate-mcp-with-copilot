# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Publicly view activity rosters
- Teacher login to sign up and unregister students

## Getting Started

1. From the repository root, install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Create a teacher account. The password is stored as a salted hash in the local,
   git-ignored `src/teachers.json` file:

   ```
   python src/create_teacher.py teacher@mergington.edu
   ```

3. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                      | Sign in as a teacher                                                |
| GET    | `/auth/session`                                                    | Check the current teacher session                                   |
| POST   | `/auth/logout`                                                     | Sign out                                                            |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher: sign up a student                                          |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher: unregister a student                                   |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

Teacher credentials are stored outside version control in `src/teachers.json`.
Passwords are salted and hashed; do not commit that file. Teacher sessions are
held in memory and expire after eight hours. Set `COOKIE_SECURE=true` when
serving the app over HTTPS.
