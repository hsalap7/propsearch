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
- Docker

### Testing & Quality
- Pytest
- React Testing Library
- Ruff (Python linting)
- Black (Python formatting)
- ESLint
- Prettier

## Project Structure

```
real-estate-map/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── repositories/# Data access layer
│   │   ├── core/        # Configuration & dependencies
│   │   └── db/          # Database setup
│   ├── tests/           # Test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/         # Database migrations
├── frontend/            # Next.js application
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├─��� database/            # Database setup & migrations
├── ingestion/           # Data ingestion framework
│   ├── base.py
│   ├── housing.py
│   ├── magicbricks.py
│   └── nobroker.py
├── docs/                # Documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/hsalap7/propsearch.git
   cd propsearch
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Add your Google Maps API key to `.env`:
   ```bash
   NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

4. Start the application:
   ```bash
   docker compose up --build
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development

### Running without Docker

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Seeding Data

```bash
cd backend
python seed.py
```

This will insert 100 sample Bangalore properties across various localities.

## API Documentation

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok"
}
```

### List Properties
```
GET /api/properties
```

Query Parameters:
- `locality` (optional): Filter by locality
- `min_price` (optional): Minimum price in rupees
- `max_price` (optional): Maximum price in rupees
- `bedrooms` (optional): Number of bedrooms
- `property_type` (optional): Type of property (apartment, villa, etc.)

Example:
```
GET /api/properties?locality=Whitefield&bedrooms=3&min_price=10000000
```

### Get Property Details
```
GET /api/properties/{id}
```

### Nearby Properties
```
GET /api/properties/nearby
```

Query Parameters:
- `lat` (required): Latitude
- `lng` (required): Longitude
- `radius_meters` (optional): Search radius in meters (default: 5000)

Example:
```
GET /api/properties/nearby?lat=12.9716&lng=77.5946&radius_meters=2000
```

## Testing

### Run Backend Tests

```bash
cd backend
pytest
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

### Code Quality

```bash
# Python
ruff check backend/
black backend/

# TypeScript/JavaScript
cd frontend
npm run lint
npm run format
```

## Data Ingestion

The ingestion framework supports multiple property sources:

- **Housing.com**
- **MagicBricks**
- **NoBroker**

Each source implements a standardized interface with `collect()`, `normalize()`, and `save()` methods. The framework is designed to be easily extensible for additional sources.

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`: Google Maps API key
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_USER`: Database user

## Contributing

Contributions are welcome! Please ensure:

1. Code follows project style guidelines (Ruff, Black, ESLint, Prettier)
2. All tests pass
3. New features include appropriate tests
4. Commit messages are clear and descriptive

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub.
