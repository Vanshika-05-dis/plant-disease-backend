# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from jose import jwt, JWTError
# from datetime import datetime, timedelta
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# from database import SessionLocal
# from models import User as UserModel
#
#
# router = APIRouter(prefix="/auth", tags=["Auth"])
#
# # ===== CONFIG =====
# SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_IT"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
#
# # ===== FAKE USER (DB later) =====
#
#
# # ===== MODELS =====
# class User(BaseModel):
#     email: str
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
# # ===== UTILS =====
# def verify_password(plain, hashed):
#     return pwd_context.verify(plain, hashed)
# def hash_password(password: str):
#     return pwd_context.hash(password)
#
#
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#
# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db)
# ):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email = payload.get("sub")
#
#         user = db.query(UserModel).filter(UserModel.email == email).first()
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")
#
#         return user
#
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
#
# # ===== ROUTES =====
# @router.post("/login", response_model=Token)
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(UserModel).filter(
#         UserModel.email == form_data.username
#     ).first()
#
#     if not user or not verify_password(
#         form_data.password, user.hashed_password
#     ):
#         raise HTTPException(status_code=400, detail="Incorrect credentials")
#
#     token = create_access_token({"sub": user.email})
#     return {"access_token": token, "token_type": "bearer"}
#
#
# @router.get("/me")
# def read_me(current_user: dict = Depends(get_current_user)):
#     return current_user
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# @router.post("/signup")
# def signup(email: str, password: str, db: Session = Depends(get_db)):
#     user = db.query(UserModel).filter(UserModel.email == email).first()
#     if user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#
#     new_user = UserModel(
#         email=email,
#         hashed_password=hash_password(password)
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#
#     return {"message": "User created successfully"}

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User as UserModel


# ================= ROUTER =================
router = APIRouter(prefix="/auth", tags=["Auth"])


# ================= CONFIG =================
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_IT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ================= SECURITY =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ================= DB DEPENDENCY =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= Pydantic MODELS =================
class Token(BaseModel):
    access_token: str
    token_type: str


class SignupRequest(BaseModel):
    email: str
    password: str


# ================= UTILS =================
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ================= ROUTES =================
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = UserModel(
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(
        UserModel.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def read_me(current_user: UserModel = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }





