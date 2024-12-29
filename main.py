
from fastapi import FastAPI
from auth import auth_router
from forms import forms_router
from database import init_db

app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(forms_router, prefix="/forms", tags=["Forms"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Form Management System"}
