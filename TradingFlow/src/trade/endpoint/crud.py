from sqlalchemy.orm import Session

# from . import auth, models, schemas

from .auth import get_password_hash
from .schemas import UserSchema
from .models import UserModel


def create_user(db: Session, user: UserSchema):
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role.value,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(UserModel).all()


def get_users_by_username(db: Session, username: str):
    return (
        db.query(UserModel).filter(UserModel.username == username).first()
    )
