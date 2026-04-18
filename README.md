
# Event-Driven Task Processing System

[![Tests](https://img.shields.io/badge/tests-14%2F14%20passing-brightgreen)](./tests)
[![Coverage](https://img.shields.io/badge/coverage-62%25-yellowgreen)](./htmlcov)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.135-009688)](https://fastapi.tiangpio.com/)

Production-grade asynchronous task processing microservice demonstrating real-world backend engineering: REST APIs, database integration, message queues, background workers, and external API consumption.

## Features

- **FastAPI REST API** with full CRUD operations
- **PostgreSQL** database with SQLAlchemy ORM
- **Redis** message broker + **Celery** distributed workers
- **Real OpenWeatherMap API** integration with error handling
- **Flower** monitoring dashboard for task execution
- **Comprehensive tests**: 14/14 passing, 62% coverage
- **Docker Compose** for containerized deployment

## Quick Start

### Local Setup
```bash
git clone <repo>
cd my-task-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
echo "DATABASE_URL=postgresql://task_user:JOHNjohn$12345@localhost:5432/task_db" > .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env
echo "OPENWEATHER_API_KEY=your_key" >> .env

# Start 4 terminals:
# Terminal 1: PostgreSQL
sudo service postgresql start

# Terminal 2: Redis
redis-server

# Terminal 3: FastAPI
python3 -m uvicorn app.main:app --reload --port 8000

# Terminal 4: Celery Worker
celery -A app.celery_config worker --loglevel=info

# Terminal 5: Flower (optional monitoring)
celery -A app.celery_config flower --port=5555
```

### Docker Compose (One Command)
```bash
docker-compose up --build
```

Access:
- **API & Docs**: http://localhost:8000/docs
- **Flower Dashboard**: http://localhost:5555

## API Endpoints

**Create Task** (async processing)
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Get weather for London","priority":"high"}'
```

**Check Status**
```bash
curl http://localhost:8000/tasks/{task_id}
```

**Other Endpoints**
```bash
GET    /tasks          # List all tasks
GET    /tasks/{id}     # Get specific task
PUT    /tasks/{id}     # Update task
DELETE /tasks/{id}     # Delete task
```

## Architecture
API Request → FastAPI → PostgreSQL + Redis Queue → Celery Worker →
External API → Database Update → User checks status anytime

**Task Flow**: pending → in_progress → completed

## Testing

```bash
pytest tests/ -v --cov=app --cov-report=html
# Result: 14 passed, 62% coverage
```

Tests cover:
- API endpoints (create, read, update, delete)
- Database model validation
- Celery task processing
- Error handling & validation

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI 0.135 |
| Database | PostgreSQL 16 + SQLAlchemy |
| Message Queue | Redis 7 |
| Task Workers | Celery 5.3 |
| Monitoring | Flower 2.0 |
| Testing | Pytest 9.0 |
| Containerization | Docker Compose |
| External API | OpenWeatherMap |

## Project Structure
app/
├── main.py          # FastAPI app, logging, lifecycle
├── routes.py        # API endpoints with validation
├── models.py        # SQLAlchemy Task model
├── database.py      # PostgreSQL connection
├── tasks.py         # Celery background tasks
├── celery_config.py # Celery + Redis setup
└── logging_config.py # Structured logging
tests/
├── test_routes.py   # API endpoint tests
├── test_models.py   # Database tests
├── test_tasks.py    # Celery tests
└── conftest.py      # Pytest fixtures

## What This Demonstrates

For hiring managers, this project showcases:

✅ **API Design** - RESTful endpoints with proper HTTP status codes
✅ **Database Design** - Normalized schema with ORM abstraction  
✅ **Async Architecture** - Non-blocking request handling at scale
✅ **Message Queues** - Industry-standard task distribution (Redis + Celery)
✅ **Background Workers** - Decoupled processing from API layer
✅ **External API Integration** - Real-world data consumption with error handling
✅ **Error Handling** - Graceful failure modes, transaction rollback, validation
✅ **Logging & Monitoring** - Production observability (file + console + Flower)
✅ **Testing** - Comprehensive coverage with fixtures and mocking
✅ **DevOps** - Docker containerization, environment configuration

**Suitable for**: Backend Engineer, Full-Stack, DevOps/SRE, Startup CTO roles

## Dependencies
fastapi==0.135.3
uvicorn==0.43.0
sqlalchemy==2.0.49
psycopg2-binary==2.9.11
python-dotenv
pydantic==2.12.5
celery==5.3.4
redis==7.4.0
requests
flower==2.0.1
pytest==7.4.3
pytest-cov==4.1.0

## Production Checklist

- [x] Full CRUD API
- [x] Database persistence
- [x] Async task processing
- [x] Real API integration
- [x] Error handling & logging
- [x] Test coverage (62%)
- [x] Containerization
- [x] Monitoring dashboard
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Rate limiting
- [ ] Authentication (JWT)
- [ ] Deployment (AWS/Heroku/GCP)

## License

MIT

---

**Built with FastAPI, PostgreSQL, Redis, Celery, Docker** 🚀
