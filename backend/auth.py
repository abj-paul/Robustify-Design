from fastapi import Request, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Constants for token handling
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token blacklist
blacklisted_tokens = set()

# Middleware for authentication
async def authenticate_request(request: Request, call_next):
    excluded_paths = ["/login", "/register", "/logout"]
    if request.url.path in excluded_paths or request.method == "OPTIONS":
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="No authorization token")

    try:
        token = auth_header.split(" ")[1]
        if token in blacklisted_tokens:
            raise HTTPException(status_code=401, detail="Token has been invalidated")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Optionally add the user information to request state
        request.state.user = username
    except (IndexError, JWTError):
        raise HTTPException(status_code=401, detail="Invalid token")

    return await call_next(request)

# Token utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)