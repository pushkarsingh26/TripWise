# Tripwise

Tripwise is a free multi-agent AI travel planning system designed to generate budget-aware travel plans, transport options, accommodation suggestions, activities, itineraries, multilingual responses, and maps based on origin, destination, budget, dates, traveler count, and personal preferences.

---

## Current Phase: Phase 1 — Project Foundation

Phase 1 establishes a clean, production-ready foundation with a Python FastAPI backend service and a Next.js frontend application.

> **Note on Future Scope**: Maps, travel APIs (flights, trains, buses, hotels, destinations), LangGraph agents, LLM integrations, vector databases, PostgreSQL, authentication, payment/booking features, and advanced chat UI are intentionally **excluded** from Phase 1 and will be introduced in subsequent phases.

---

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- LangGraph
- LangChain

### Frontend
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- ESLint

---

## Project Structure

```text
tripwise/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── __init__.py
│   │   ├── agents/
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   └── __init__.py
│   │   └── config/
│   │       └── __init__.py
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── frontend/
│   ├── src/
│   │   └── app/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── .gitignore
├── README.md
└── LICENSE
```

---

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   Copy `.env.example` to `.env`.

5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the frontend development server:
   ```bash
   npm run dev
   ```

---

## Running Both Services

- **Backend API**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`
- **Frontend App**: `http://localhost:3000`

---

## Current API Endpoints

- `GET /` — Returns status message and API version.
  ```json
  {
    "message": "Tripwise API is running",
    "version": "0.1.0"
  }
  ```
- `GET /health` — Returns backend health status.
  ```json
  {
    "status": "healthy"
  }
  ```
- `GET /docs` — Standard OpenAPI documentation UI.

---

## Free LLM Providers

Tripwise supports multiple free-tier LLM providers for conversational trip modification (Phase 7):

- **Groq** (`LLM_PROVIDER=groq`)
- **NVIDIA NIM / Build** (`LLM_PROVIDER=nvidia`)
- **Google Gemini** (`LLM_PROVIDER=gemini`)
- **OpenRouter** (`LLM_PROVIDER=openrouter`)

### Configuration & Key Security
- Only one provider is active at a time, controlled via `LLM_PROVIDER` in `backend/.env`.
- API keys are managed locally in `backend/.env` and must **never** be committed to Git. `backend/.env.example` contains placeholders.
- An optional fallback provider can be enabled via `LLM_FALLBACK_PROVIDER`.
- Execution timeouts (`LLM_TIMEOUT_SECONDS`) and retries (`LLM_MAX_RETRIES`) are fully configurable.
- Core Phase 1–6 functionality works 100% deterministically without any LLM API key configured.

---

## License

[MIT License](LICENSE)

