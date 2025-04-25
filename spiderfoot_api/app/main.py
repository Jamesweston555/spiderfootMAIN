from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import subprocess
import json
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Scan(BaseModel):
    id: str
    name: str
    target: str
    status: str
    created: datetime
    started: Optional[datetime] = None
    completed: Optional[datetime] = None

class ScanCreate(BaseModel):
    name: str
    target: str
    modules: List[str]

# FastAPI app
app = FastAPI(
    title="SpiderFoot API",
    description="A REST API wrapper for SpiderFoot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    # In production, this would check a database
    if username == "admin":
        return UserInDB(
            username=username,
            hashed_password=get_password_hash("admin")
        )
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/scans", response_model=List[Scan])
async def list_scans(current_user: User = Depends(get_current_user)):
    try:
        result = subprocess.run(
            ["python", "sf.py", "-l"],
            capture_output=True,
            text=True
        )
        scans = []
        # Parse the output and create Scan objects
        # This is a placeholder - you'll need to implement proper parsing
        return scans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scans", response_model=Scan)
async def create_scan(
    scan: ScanCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        # Start a new scan
        cmd = [
            "python", "sf.py",
            "-s", scan.name,
            "-t", scan.target,
            "-m", ",".join(scan.modules)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start scan: {result.stderr}"
            )
            
        # Parse the output to get scan ID
        # This is a placeholder - you'll need to implement proper parsing
        scan_id = "generated-id"
        
        return Scan(
            id=scan_id,
            name=scan.name,
            target=scan.target,
            status="running",
            created=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans/{scan_id}", response_model=Scan)
async def get_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        # Get scan status
        cmd = ["python", "sf.py", "-q", scan_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=404,
                detail=f"Scan not found: {result.stderr}"
            )
            
        # Parse the output and create a Scan object
        # This is a placeholder - you'll need to implement proper parsing
        return Scan(
            id=scan_id,
            name="scan-name",
            target="scan-target",
            status="running",
            created=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/scans/{scan_id}")
async def delete_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        # Stop and delete the scan
        cmd = ["python", "sf.py", "-d", scan_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to delete scan: {result.stderr}"
            )
            
        return {"message": "Scan deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 