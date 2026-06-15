# Property Search - Bangalore Real Estate Map Platform

A production-grade real estate map platform for Bangalore that aggregates property listings from multiple sources and visualizes them on Google Maps.

## Features

- 🗺️ Interactive Google Maps visualization of properties
- 🔍 Advanced filtering (locality, price, bedrooms, property type)
- 📍 Geospatial search (find nearby properties)
- 🖼️ Property photo galleries
- 📋 Detailed property information
- 🔗 Direct links to source portals
- 🏗️ Extensible data ingestion framework
- 🐳 Complete Docker Compose setup for local development

## Tech Stack

### Frontend
- Next.js 15
- React 19
- TypeScript
- TailwindCSS
- Google Maps JavaScript API

### Backend
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Alembic

### Database
- PostgreSQL 16
- PostGIS (geospatial queries)

### Infrastructure
- Docker Compose

### Testing & Quality
- Pytest
- React Testing Library
- Ruff, Black, ESLint, Prettier

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Setup

1. Clone and setup:
   ```bash
   git clone https://github.com/hsalap7/propsearch.git
   cd propsearch
   cp .env.example .env
   ```

2. Add Google Maps API key to `.env`

3. Start:
   ```bash
   docker compose up --build
   ```

4. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Documentation

See [docs/](./docs/) for detailed documentation.

## Property Ingestion

The backend includes a Playwright-first, registry-driven ingestion pipeline for
Housing.com, NoBroker, MagicBricks, and 99acres. Collectors retain every raw
payload before normalization, then centrally deduplicate, geocode, and save
canonical properties.

Configure source search pages as JSON:

```bash
export COLLECTOR_SEARCH_URLS='{"housing":["https://housing.com/..."],"nobroker":["https://nobroker.in/..."]}'
export GOOGLE_GEOCODING_API_KEY='optional-key'
```

Run one source or the scheduler from `backend/`:

```bash
python collect.py housing
python collect.py nobroker
python scheduler.py
```

Apply the database migration before collecting:

```bash
alembic upgrade head
```

The scheduler runs Housing.com and MagicBricks every 6 hours, and NoBroker and
99acres every 12 hours. Each portal's terms, robots policy, and applicable law
must be reviewed before adding production search URLs. Prefer permitted
structured APIs or intercepted JSON responses over rendered HTML.

Operational counts are available at `GET /admin/stats`.
