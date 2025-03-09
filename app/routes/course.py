from datetime import datetime, timedelta
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session, joinedload

from app.models import get_db
from app.models.models import Course, Lesson

router = APIRouter()


class LessonBase(BaseModel):
    start_time: datetime
    end_time: datetime


class LessonCreate(LessonBase):
    pass


class LessonResponse(LessonBase):
    id: int


class ResponseLessonList(BaseModel):
    items: List[LessonResponse]


# Pydantic models for request/response
class CourseBase(BaseModel):
    teacher_id: int
    program_id: int
    comment: Optional[str] = None
    is_active: bool = True


class CourseSchedule(BaseModel):
    date: str
    start_time: str
    end_time: str
    recurring: Literal["daily", "weekly", "monthly", "weekdays", "weekends"]
    recurring_end_date: Optional[str] = None


class CourseCreate(CourseBase):
    schedule: List[CourseSchedule]


class CourseUpdate(CourseBase):
    pass


class TeacherResponse(BaseModel):
    id: int
    name: str


class ProgramResponse(BaseModel):
    id: int
    name: str


class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    lessons: List[LessonResponse] = []
    teacher: TeacherResponse
    program: ProgramResponse

    @model_validator(mode="after")
    def order_lessons(self):
        self.lessons.sort(key=lambda x: x.start_time)
        return self


class CourseListResponse(BaseModel):
    items: List[CourseResponse]


def generate_schedule(schedule: CourseSchedule) -> List[str]:
    start_date = datetime.strptime(schedule.date, "%Y-%m-%d")
    end_date = (
        datetime.strptime(schedule.recurring_end_date, "%Y-%m-%d")
        if schedule.recurring_end_date
        else None
    )

    start_time = schedule.start_time
    end_time = schedule.end_time

    current_date = start_date
    schedule_dates = []

    while end_date is None or current_date <= end_date:
        schedule_dates.append(
            {
                "start": f"{current_date.strftime('%Y-%m-%d')} {start_time}:00",
                "end": f"{current_date.strftime('%Y-%m-%d')} {end_time}:00",
            }
        )

        if schedule.recurring == "daily":
            current_date += timedelta(days=1)
        elif schedule.recurring == "weekly":
            current_date += timedelta(weeks=1)
        elif schedule.recurring == "monthly":
            next_month = current_date.month % 12 + 1
            year = current_date.year + (1 if next_month == 1 else 0)
            current_date = current_date.replace(year=year, month=next_month)
        elif schedule.recurring == "weekdays":
            current_date += timedelta(days=1)
            while current_date.weekday() in [5, 6]:  # Skip weekends
                current_date += timedelta(days=1)
        elif schedule.recurring == "weekends":
            current_date += timedelta(days=1)
            while current_date.weekday() not in [5, 6]:  # Skip weekdays
                current_date += timedelta(days=1)

    return schedule_dates


@router.get("", response_model=CourseListResponse)
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = (
        db.query(Course)
        .filter(Course.is_active == 1)
        .join(Course.teacher)
        .join(Course.program)
        .options(
            joinedload(Course.teacher),
            joinedload(Course.program),
            joinedload(Course.lessons),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {"items": courses}


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    try:
        db_course = Course(
            teacher_id=course.teacher_id,
            program_id=course.program_id,
            schedule=[i.model_dump() for i in course.schedule],
            is_active=course.is_active,
        )
        db.add(db_course)
        db.commit()

        for schedule in course.schedule:
            schedule_dates = generate_schedule(schedule)
            for date in schedule_dates:
                db_lesson = Lesson(
                    course_id=db_course.id,
                    start_time=date["start"],
                    end_time=date["end"],
                )
                db.add(db_lesson)
            db.commit()
            db.refresh(db_course)
            return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = (
        db.query(Course)
        .join(Course.teacher)
        .join(Course.program)
        .options(
            joinedload(Course.teacher),
            joinedload(Course.program),
            joinedload(Course.lessons),
        )
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程未找到")

    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db)
):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程未找到")

    for key, value in course_update.dict().items():
        setattr(db_course, key, value)

    db.commit()
    db.refresh(db_course)
    return db_course


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程未找到")

    db_course.is_active = False
    db.commit()
    return {"success": True}


@router.get("/course/{course_id}/lessons", response_model=ResponseLessonList)
def get_lessons(course_id: int, db: Session = Depends(get_db)):
    lessons = (
        db.query(Lesson)
        .filter(Lesson.course_id == course_id)
        .order_by(Lesson.start_time.desc())
        .all()
    )
    return lessons


@router.post(
    "/course/{course_id}/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(course_id: int, lesson: LessonCreate, db: Session = Depends(get_db)):
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.delete("/course/{course_id}/lesson/{lesson_id}")
def delete_lesson(course_id: int, lesson_id: int, db: Session = Depends(get_db)):
    db_lesson = (
        db.query(Lesson)
        .filter(Lesson.course_id == course_id, Lesson.id == lesson_id)
        .first()
    )
    if not db_lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程未找到")

    db.delete(db_lesson)
    db.commit()
    return {"success": True}
