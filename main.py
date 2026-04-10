from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# ── Import all models so SQLAlchemy creates tables on startup ──
from models.auth      import User
from models.disaster  import DisasterReport, HelpRequest
from models.volunteer import Volunteer, Assignment, Resource
from models.location  import Location
from models.notification import Notification

# ── Import all routers ──
from routes import auth, disaster, volunteer, maps

app = FastAPI(
    title="Disaster Relief Coordination System",
    description="Full API for coordinating disaster relief across 4 modules.",
    version="1.0.0"
)

# ── CORS — allows the frontend HTML files to call the API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Create all tables on startup ──
Base.metadata.create_all(bind=engine)

# ── Register all routers ──
app.include_router(auth.router)
app.include_router(disaster.router)
app.include_router(volunteer.router)
app.include_router(maps.router)


@app.get("/")
def root():
    return {
        "message": "Disaster Relief Coordination System is running.",
        "modules": [
            "Auth & Users        → /auth",
            "Disaster & Requests → /disaster",
            "Volunteers          → /volunteers",
            "Maps & Notifications→ /maps"
        ],
        "docs": "/docs"
    }