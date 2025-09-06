# Secure Task Tracker

A secure task management API built with FastAPI and PostgreSQL.

## Quick Start

### Docker
```bash
docker-compose up -d
```

### Local Development
```bash
pip install -r requirements.txt
alembic upgrade head
fastapi dev ./app/main.py
```

## API Documentation

Once running, visit:

- API Docs: http://localhost:8000/docs

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `SECRET_KEY`
- `ENV` (development/production)