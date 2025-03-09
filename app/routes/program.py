from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.models import Program
from app.utils.jwt_utils import get_current_user

router = APIRouter()


class ProgramBase(BaseModel):
    category: str
    name: str
    description: str = None
    comment: str = None
    is_active: Optional[bool] = True


class ProgramCreate(ProgramBase):
    pass


class ProgramResponse(ProgramBase):
    id: int

    class Config:
        orm_mode = True


class ResponseProgramList(BaseModel):
    items: List[ProgramResponse]


# 创建课程教师
@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    existing = (
        db.query(Program)
        .filter(
            Program.category == program.category, Program.name == program.name
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course teacher already exists",
        )
    db_program = Program(**program.model_dump())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


# 获取单个课程教师
@router.get("/{program_id}", response_model=ProgramResponse)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Program not found"
        )
    return program


# 获取课程教师列表
@router.get("", response_model=ResponseProgramList)
def list_programs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    programs = (
        db.query(Program)
        .filter(Program.is_active == 1)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "items": programs,
    }


# 更新课程教师
@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: int,
    program: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_program = (
        db.query(Program).filter(Program.id == program_id).first()
    )
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Program not found"
        )

    for key, value in program.model_dump().items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program


# 删除课程教师（软删除）
@router.delete("/{program_id}")
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_program = (
        db.query(Program).filter(Program.id == program_id).first()
    )
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Program not found"
        )

    db_program.is_active = False
    db.commit()
    return {
        "success": True,
    }
