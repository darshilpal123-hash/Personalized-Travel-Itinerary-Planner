# Personalized Travel Itinerary Planner

**Skill Wallet Capstone Project 4** — Streamlit travel-planning app with destination recommendations, day-wise itinerary generation, route clustering, activity swaps, session-based trip history and offline PDF export.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`). Demo mode works without API keys.

## AI provider keys

The app can run in built-in demo mode or accept Gemini/Groq API keys in the sidebar. Keys entered in the UI are held in session state only and are not saved with trips. For deployment, prefer Streamlit secrets:

`.streamlit/secrets.toml`

```toml
GEMINI_API_KEY = "your-key"
GROQ_API_KEY = "your-key"
```

Never commit a real secrets file to source control. Streamlit Community Cloud supports app secrets in its settings.

## Deploy on Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, and this README to a GitHub repository.
2. In Streamlit Community Cloud, create an app from the repository and select `app.py` as the entry point.
3. Add provider keys through the app's Secrets settings if needed. Demo mode needs no secrets.

## Included modules

- Preference form: destination or open-ended vibe, duration, start date, budget, party, pace, interests and optional custom instructions.
- Top-three destination shortlist using simple season-window, vibe, budget and tag heuristics.
- Day-by-day time slots with proximity-aware nearest-neighbour ordering for built-in cities and estimated costs in local currency plus USD/INR comparisons.
- Per-slot activity customization and single-day regeneration without replacing other days.
- Multiple trip snapshots in Streamlit session state, history/load controls, and a ReportLab PDF export with emergency checklist.

## Important implementation notes

- **Persistence:** history is simulated in Streamlit session state; it survives reruns in a session but is not durable across server restarts/new sessions. This is intentional to avoid an external database dependency. For durable production storage, add a managed persistence layer.
- **Routing:** clustering uses haversine distance and a nearest-neighbour heuristic against bundled approximate coordinates; it is not a live maps/routing engine. For arbitrary user-entered destinations, location clustering falls back safely to generic suggestions.
- **Rates and costs:** FX conversion factors and activity costs are illustrative static planning estimates, not live market data or vendor quotes.
- **AI:** the optional provider call is currently used as a connectivity/augmentation hook; itinerary rendering stays deterministic for reliable structure. Do not present estimates as bookings or confirmed availability.
- **Production readiness:** before real customer use, add automated tests, rate limits, privacy notice/retention controls, monitoring, live geocoding/routing and authoritative source integrations. No app can guarantee travel safety or real-time accuracy from bundled sample data alone.
