from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import uuid
from db_operation.mongo_crud import users
from logging_module.application_logging import logger


# JWT Configurations
SECRET_KEY = "Your-Secret-Key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User Model
class User(BaseModel):
    email: str
    password: str
    confirm_password:str=None


# JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    except Exception as ex:
        logger.info("failed to create_access_token")
        return {"message":"failed to create_access_token","status":"failed"}


# Get User from MongoDB
def get_user(email: str):
    try:
        user = users.find_one({"email": email})
        if user:
            return User(**user)
        else:
            return None
    except Exception as ex:
        logger.info("failed to get_user")
        return {"message":"failed to get_user","status":"failed"}


# Hash Password
def hash_password(password: str):
    try:
        return pwd_context.hash(password)
    except Exception as ex:
        logger.info("failed to hash_password")
        return {"message":"failed to hash_password","status":"failed"}


# Verify Password
def verify_password(plain_password: str, hashed_password: str):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as ex:
        logger.info("failed to verify_password")
        return {"message":"failed to verify_password","status":"failed"}


# Create User
def create_user(email,password):
    try:
        hashed_password = hash_password(password)
        new_user = {}
        random_uuid = uuid.uuid4()
        hex_uuid = random_uuid.hex
        
        new_user.update({"password":hashed_password})
        new_user.update({"user_id":hex_uuid})
        new_user.update({"email":email})

        new_user.update({"created_at":datetime.utcnow()})
        users.insert_one(new_user)
        return new_user
    
    except Exception as ex:
        logger.info("failed to create_user")
        return {"message":"failed to create_user","status":"failed"}
