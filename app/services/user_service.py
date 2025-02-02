from hashlib import sha256

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.model.models import User
from app.schemas.schemas import UserCreate


class UserService:
    @staticmethod
    def create_user(user: UserCreate, db: Session):
        hashed_password = sha256(user.password.encode()).hexdigest()
        new_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(username: str, password: str, db: Session):
        hashed_password = sha256(password.encode()).hexdigest()
        user = db.query(User).filter(User.username == username, User.password_hash == hashed_password).first()
        return user

    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def get_user_by_username(username: str, db: Session):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
