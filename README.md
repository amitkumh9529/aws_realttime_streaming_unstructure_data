# 🌴 Holiday Planner — AI-Powered Travel SaaS

A full-stack SaaS application for intelligent holiday planning, featuring AI itinerary generation, flight/hotel price prediction, weather-based recommendations, and a smart budget optimizer.

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, React Query |
| Backend | FastAPI (Python), Celery, Pydantic |
| Database | PostgreSQL 16, Redis 7 |
| ML/AI | XGBoost, scikit-learn, OpenAI GPT-4o |
| Infra | Docker Compose, Nginx |

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose installed
- Git

### 1. Clone and configure environment
```bash
git clone <your-repo>
cd holiday-planner

# Copy environment variables
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET
# - OPENWEATHER_API_KEY
nano .env
```

### 2. Start all services
```bash
docker-compose up --build
```

This will start:
- 🌐 **Frontend** → http://localhost:3000
- ⚡ **Backend API** → http://localhost:8000
- 📚 **API Docs** → http://localhost:8000/docs
- 🗄️ **PostgreSQL** → localhost:5432
- 📦 **Redis** → localhost:6379
- 🔀 **Nginx** → http://localhost:80

### 3. Local development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
holiday-planner/
├── frontend/           # Next.js 14 app
│   ├── app/            # App Router pages
│   ├── components/     # Reusable UI components
│   └── lib/            # API client, utilities
│
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/        # Route handlers
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   └── core/       # Config, DB, security
│   └── ml/             # ML models
│       ├── price_predictor/
│       ├── weather/
│       ├── itinerary/
│       └── budget/
│
└── infra/              # Nginx, DB init scripts
```

---

## 🤖 ML Models

| Model | Algorithm | Status |
|-------|-----------|--------|
| Flight Price Predictor | XGBoost + rule-based | MVP (rule-based, replace with trained model) |
| Hotel Price Predictor | XGBoost + rule-based | MVP |
| Itinerary Generator | GPT-4o | Ready (needs API key) |
| Weather Recommender | K-Means + climate DB | MVP |
| Budget Optimizer | Linear Programming (PuLP) | Phase 2 |

---

## 🔑 API Keys Needed

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| OpenAI | Itinerary generation | $5 free credits |
| Amadeus | Real flight data | Yes — sandbox |
| OpenWeatherMap | Weather data | Yes — 1000 calls/day |
| Google Places | Location search | $200/month credit |

---

## 📋 Development Roadmap

- [x] **Phase 1**: Monorepo setup, Docker, DB models, Auth API
- [ ] **Phase 2**: ML models with real training data
- [ ] **Phase 3**: Frontend dashboard, trip planner UI
- [ ] **Phase 4**: Payment integration (Stripe), deployment

---

## 🧪 API Testing

Visit http://localhost:8000/docs for interactive Swagger UI.

Quick test:
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=test@example.com&password=password123"
```
