
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session, User
from passlib.hash import bcrypt
from fastapi.responses import JSONResponse
from sqlalchemy.future import select


auth_router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

async def authenticated_user(
    request: Request, session: AsyncSession = Depends(get_session)
):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user.id

@auth_router.post("/register")
async def register(user: RegisterRequest, session: AsyncSession = Depends(get_session)):
    # check if the user already exists
    stmt = select(User).where(User.email == user.email)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()  # Get one result or None
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(user.password)
    
    # Create a new user object
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    session.add(new_user)
    
    # Commit the transaction to save the user
    await session.commit()
    
    return {"message": "User registered successfully"}

@auth_router.post("/login")
async def login(credentials: LoginRequest, session: AsyncSession = Depends(get_session)):
    try:
        # Query to find the user by email
        stmt = select(User).where(User.email == credentials.email)
        result = await session.execute(stmt)
        user = result.scalars().first()  # Extract the first user
        
        # Check if the user exists and if the password matches
        if not user or not bcrypt.verify(credentials.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Create a response with a cookie
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(key="user_id", value=str(user.id))
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the request")

@auth_router.post("/logout")
async def logout(request: Request):
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("user_id")
    return response
