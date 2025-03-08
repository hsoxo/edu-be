from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import get_db
from app.models.models import CourseTeacher
from pydantic import BaseModel
from app.utils.jwt_utils import get_current_user

router = APIRouter()

class CourseTeacherBase(BaseModel):
    category: str
    program: str
    teacher: str
    summary: str = None
    is_active: Optional[bool] = True

class CourseTeacherCreate(CourseTeacherBase):
    pass

class CourseTeacherResponse(CourseTeacherBase):
    id: int

    class Config:
        orm_mode = True

class ResponseCourseTeacherList(BaseModel):
    items: List[CourseTeacherResponse]

# 创建课程教师
@router.post("", response_model=CourseTeacherResponse, status_code=status.HTTP_201_CREATED)
def create_course_teacher(
    course_teacher: CourseTeacherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing = db.query(CourseTeacher).filter(CourseTeacher.teacher == course_teacher.teacher and
                                              CourseTeacher.category == course_teacher.category and
                                              CourseTeacher.program == course_teacher.program).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course teacher already exists"
        )
    db_course_teacher = CourseTeacher(**course_teacher.model_dump())
    db.add(db_course_teacher)
    db.commit()
    db.refresh(db_course_teacher)
    return db_course_teacher

# 获取单个课程教师
@router.get("/{teacher_id}", response_model=CourseTeacherResponse)
def get_course_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    course_teacher = db.query(CourseTeacher).filter(CourseTeacher.id == teacher_id).first()
    if not course_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course teacher not found"
        )
    return course_teacher

# 获取课程教师列表
@router.get("", response_model=ResponseCourseTeacherList)
def list_course_teachers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    course_teachers = db.query(CourseTeacher).filter(CourseTeacher.is_active == 1).offset(skip).limit(limit).all()
    return {
        "items": course_teachers,
    }

# 更新课程教师
@router.put("/{teacher_id}", response_model=CourseTeacherResponse)
def update_course_teacher(
    teacher_id: int,
    course_teacher: CourseTeacherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_course_teacher = db.query(CourseTeacher).filter(CourseTeacher.id == teacher_id).first()
    if not db_course_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course teacher not found"
        )
    
    for key, value in course_teacher.model_dump().items():
        setattr(db_course_teacher, key, value)
    
    db.commit()
    db.refresh(db_course_teacher)
    return db_course_teacher

# 删除课程教师（软删除）
@router.delete("/{teacher_id}")
def delete_course_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_course_teacher = db.query(CourseTeacher).filter(CourseTeacher.id == teacher_id).first()
    if not db_course_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course teacher not found"
        )
    
    db_course_teacher.is_active = False
    db.commit()
    return {
        "success": True,
    }
