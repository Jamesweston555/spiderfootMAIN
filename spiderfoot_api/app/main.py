from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import requests
import os

# Security settings
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SpiderFoot API settings
SPIDERFOOT_API_URL = f"http://localhost:{os.getenv('SPIDERFOOT_API_PORT', '5001')}"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Scan(BaseModel):
    id: str
    name: str
    target: str
    status: str
    created: datetime

class ScanCreate(BaseModel):
    name: str
    target: str
    modules: List[str]

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Security functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

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
    return token_data

# Routes
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real application, you would verify the credentials against a database
    # For this example, we'll use a hardcoded user
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/scans", response_model=List[Scan])
async def list_scans(current_user: TokenData = Depends(get_current_user)):
    try:
        response = requests.get(f"{SPIDERFOOT_API_URL}/scanlist")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scans", response_model=Scan)
async def create_scan(scan: ScanCreate, current_user: TokenData = Depends(get_current_user)):
    try:
        data = {
            "scanname": scan.name,
            "scantarget": scan.target,
            "usecase": "all",
            "modulelist": ",".join(scan.modules)
        }
        response = requests.post(f"{SPIDERFOOT_API_URL}/startscan", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans/{scan_id}", response_model=Scan)
async def get_scan(scan_id: str, current_user: TokenData = Depends(get_current_user)):
    try:
        response = requests.get(f"{SPIDERFOOT_API_URL}/scanstatus", params={"id": scan_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str, current_user: TokenData = Depends(get_current_user)):
    try:
        response = requests.post(f"{SPIDERFOOT_API_URL}/scandelete", params={"id": scan_id})
        response.raise_for_status()
        return {"status": "success"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=404, detail=str(e))

# Proxy all other requests to SpiderFoot API
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(path: str, request: Request, current_user: TokenData = Depends(get_current_user)):
    try:
        url = f"{SPIDERFOOT_API_URL}/{path}"
        headers = dict(request.headers)
        headers.pop("host", None)
        
        if request.method == "GET":
            response = requests.get(url, params=dict(request.query_params), headers=headers)
        elif request.method == "POST":
            response = requests.post(url, json=await request.json(), headers=headers)
        elif request.method == "PUT":
            response = requests.put(url, json=await request.json(), headers=headers)
        elif request.method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
            
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 