from sqlalchemy.orm import Session
from app.models.user import User
from app.services.security_service import SecurityService


class UserService:

    @staticmethod
    def list_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(
            User.email == email
        ).first()

    @staticmethod
    def get_by_username(db: Session, username: str):
        return db.query(User).filter(
            User.username == username
        ).first()

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        role: str = "USER"
    ):

        hashed_password = SecurityService.hash_password(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role=role
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate(
        db: Session,
        username: str,
        password: str
    ):

        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if user is None:
            return None

        if not SecurityService.verify_password(
            password,
            user.password
        ):
            return None

        return user