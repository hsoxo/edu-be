from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.models import Student, StudentLesson

router = APIRouter()


# Pydantic models for request/response
class StudentBase(BaseModel):
    name: str
    email: str
    phone: str
    is_active: bool = True


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class StudentLessonBase(BaseModel):
    student_id: int
    lesson_id: int
    is_active: bool = True


class StudentLessonResponse(StudentLessonBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResponseStudentLessonList(BaseModel):
    items: List[StudentLessonResponse]


class StudentLessonCreate(StudentLessonBase):
    pass


@router.get("", response_model=ResponseStudentLessonList)
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return {"items": students}


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生未找到")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生未找到")

    for key, value in student_update.dict().items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生未找到")

    db.delete(db_student)
    db.commit()
    return {"success": True}


@router.get("/{student_id}/lessons", response_model=ResponseStudentLessonList)
def get_lessons(student_id: int, db: Session = Depends(get_db)):
    lessons = (
        db.query(StudentLesson)
        .filter(StudentLesson.student_id == student_id)
        .order_by(StudentLesson.created_at.desc())
        .all()
    )
    return lessons


@router.post(
    "/{student_id}/lessons",
    response_model=StudentLessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    student_id: int, lesson: StudentLessonCreate, db: Session = Depends(get_db)
):
    db_lesson = StudentLesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.delete("/{student_id}/lesson/{lesson_id}")
def delete_lesson(student_id: int, lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = (
        db.query(StudentLesson)
        .filter(StudentLesson.student_id == student_id, StudentLesson.id == lesson_id)
        .first()
    )
    if not db_lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程未找到")

    db.delete(db_lesson)
    db.commit()
    return {"success": True}
