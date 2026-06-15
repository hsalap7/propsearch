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

## Documentation

See [docs/](./docs/) for detailed documentation.
