# Dating Backend

Django REST API for account management, dating profiles, matching, chat, notifications, reporting, and subscriptions.
and provide inforamtion for storing
## Run locally

```powershell
.\env\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

The development server is available at `http://127.0.0.1:8000/`.

## Deployment settings

Set these environment variables in production. A template is available in `.env.example`; Django does not read `.env` files automatically, so configure them through your host or process manager.

```text
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.example.com
```

The application refuses to start with `DJANGO_DEBUG=False` unless `DJANGO_SECRET_KEY` and at least one allowed host are configured.

For production, also configure the `POSTGRES_*` variables in `.env.example`. The app switches to PostgreSQL whenever `POSTGRES_DB` is set and refuses to use SQLite with debug disabled. Run migrations and collect static files during deployment:

```powershell
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

`STATIC_ROOT` is `staticfiles/` and user uploads use `media/`. Configure persistent storage and automated backups for both PostgreSQL and uploaded media in your hosting platform before launch. Application logs are written to standard output and can be collected by the hosting platform.

## Test

```powershell
.\env\Scripts\python.exe manage.py test
```

## OpenAPI schema

Start the development server and open `http://127.0.0.1:8000/api/schema/` for the machine-readable OpenAPI schema. Import this endpoint into Postman, Insomnia, or a Swagger-compatible client to explore the API.

## Core API flow

1. Create an account: `POST /api/auth/register/`
2. Obtain JWT tokens: `POST /api/auth/login/`
3. Send `Authorization: Bearer <access-token>` with protected requests.
4. View or update the user's profile: `GET` or `PATCH /api/profiles/me/`
5. Send a match request: `POST /api/matches/request/` with `{"recipient": <user-id>}`.
6. The recipient accepts it: `POST /api/matches/<match-id>/action/` with `{"action": "accept"}`.
7. Start a chat after acceptance: `POST /api/chats/start/` with `{"recipient": <user-id>}`.

Match requests, accepted matches, and new chat messages automatically create in-app notifications for the affected user.

## Key endpoints

| Area | Endpoint |
| --- | --- |
| Authentication | `/api/auth/register/`, `/api/auth/login/`, `/api/auth/me/` |
| Profiles | `/api/profiles/`, `/api/profiles/me/` |
| Matches | `/api/matches/`, `/api/matches/request/`, `/api/matches/<id>/action/` |
| Chats | `/api/chats/`, `/api/chats/start/`, `/api/chats/<id>/messages/` |
| Notifications | `/api/notifications/`, `/api/notifications/unread-count/`, `/api/notifications/<id>/read/` |
