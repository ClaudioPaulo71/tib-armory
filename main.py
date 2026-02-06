from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Imports
from database import create_db_and_tables 
from apps.armory.router import router as armory_router
from apps.auth.router import router as auth_router
from apps.auth.webhook_router import router as webhook_router
from apps.auth.deps import get_current_user

# Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="TIB Armory", lifespan=lifespan)

# Session Middleware (Auth0)
SECRET_KEY = os.getenv("SECRET_KEY", "armory_secret_key")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(auth_router)
app.include_router(armory_router)
app.include_router(webhook_router)

# Root -> Redirect to Armory Dashboard or Portal
@app.get("/")
def home(request: Request):
    # If using reverse proxy, this might be accessed via tib-usa.app/armory/
    return RedirectResponse(url="/armory")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
