from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Enum,
    Boolean,
    DateTime,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext

from . import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    to_email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)


class CourseTeacher(Base):
    __tablename__ = "course_teachers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(255), nullable=False)
    program = Column(String(255), nullable=False)
    teacher = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, nullable=True)
    schedule_time = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(Enum("M", "F", "Other"), default="Other")
    phone = Column(String(20), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    to_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(Enum("pending", "sent", "failed"), default="pending")
    error_msg = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    sent_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User")


class EnrollmentRequest(Base):
    __tablename__ = "enrollment_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(Enum("pending", "approved", "rejected"), default="pending")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")
    course = relationship("Course")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    leave_date = Column(TIMESTAMP, nullable=False)
    status = Column(Enum("pending", "approved", "rejected"), default="pending")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")
    course = relationship("Course")


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(Enum("pending", "approved", "rejected"), default="pending")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")
    course = relationship("Course")


class UserCourse(Base):
    __tablename__ = "user_courses"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User")
    course = relationship("Course")
