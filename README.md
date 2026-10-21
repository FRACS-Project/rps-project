# RPS: Recipe · Planning · Shopping

**English** · [Français](README.fr.md)

A backend for a cooking app where users manage their recipes, plan meals and build shopping lists. The long-term goal is a small social network around cooking.

> **Status: alpha, in active development.** The recipe domain and authentication are working. Planning, shopping and pantry ("fridge") are on the roadmap.

## Tech stack

| Area | Tools |
|---|---|
| API | Python 3.12, FastAPI, Pydantic |
| Data | SQLModel (SQLAlchemy), PostgreSQL 15 |
| Auth | OAuth2 password flow, JWT (python-jose), bcrypt (passlib) |
| Infra | Docker, Docker Compose, Nginx reverse proxy |
| Tooling | uv, pytest |

A Flutter mobile client is developed separately and is not part of this repository.

## Features

- **Authentication**: signup, then login by username or email (OAuth2 form or JSON). Requests are authenticated with JWT bearer tokens.
- **Users**: admin and disabled-account flags. User management is restricted to admins.
- **Recipes**: full CRUD, with ingredients, ordered instructions, tags and images.
- **Bookmarks**: users can save recipes to their own list.
- **Ownership**: `/me` endpoints only ever read or change the current user's own resources.
- **Shared catalogue**: ingredients and tags. Write access is restricted to admins.

### Security choices

- Passwords are hashed with bcrypt. The policy requires 12+ characters with upper and lower case, a digit and a special character.
- Usernames are validated and emails are normalised.
- Image uploads are checked by their real MIME type (python-magic), not by file extension. Nginx caps request bodies at 10 MB.
- The API container runs as a non-root user and is only reachable through Nginx, never directly from the host.
- All secrets come from environment variables. None are committed.

## Architecture

The code is organised by domain. Each domain follows the same layers:

```
routers  →  services  →  crud  →  models
(HTTP)      (rules)       (DB)    (SQLModel tables)
```

Each domain also has `schemas` (input/output models) and its own `exceptions`.

```
apps/api/
├── auth/            # login, signup, JWT
├── user/
├── recipe/
│   └── components/  # instruction, recipe_ingredient, recipe_tag
├── shared/          # ingredient, tag, image, bookmark
├── planning/        # roadmap
├── shopping/        # roadmap
├── core/            # config, security, paths
├── db/              # engine and session
└── main.py
docker/              # nginx config, container entrypoint
tests/
```

## Getting started

### With Docker (recommended)

```bash
cp .env.example .env
# edit .env: set SECRET_KEY (openssl rand -hex 32) and POSTGRES_PASSWORD
docker compose up --build
```

The API is served through Nginx at **http://localhost:8080**. Interactive docs are at **http://localhost:8080/docs**.

The stack runs three services: `db` (PostgreSQL), `backend` (FastAPI/uvicorn) and `nginx`. Database tables are created on startup.

### Running the tests

```bash
uv sync
uv run pytest
```

The tests use an in-memory SQLite database. They do not need Docker or PostgreSQL.

## API overview

| Prefix | Purpose |
|---|---|
| `/auth` | `signup`, `login`, `login-json`, `me` |
| `/users` | user management (admin) |
| `/recipe` | recipes; `/recipe/me` for the current user's recipes |
| `/recipe_ingredient`, `/instruction` | recipe components |
| `/ingredient`, `/tag` | shared catalogue |
| `/bookmark/me` | saved recipes |
| `/image` | recipe images |

See `/docs` for the full, up-to-date schema.

## Roadmap

- [ ] Planning, Shopping and Fridge modules
- [ ] HTTPS on Nginx
- [ ] Wider test suite (integration tests, more coverage)
- [ ] Self-hosted deployment on a Linux home server with remote access via Tailscale
