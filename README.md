# Yacht Club

Web application for managing a sailing club - members, boats, events, and work tasks.

## Features
- User authentication (login/register)
- Member management with roles and sailing licenses
- Boat fleet management
- Event creation and sign-ups
- Work task organization


## Tech Stack
- Python + Django
- Bootstrap 4
- Django Soft Ui Design
- SQLite (default)


## Setup
1. `pip install -r requirements.txt`
2. `python manage.py migrate`

## Testing data
1. `python manage.py loaddata test_data/yacht_club.json`
2. Copy `test_data/media` to project root
3. `python manage.py runserver`
4. username: `admin` | password: `password`
