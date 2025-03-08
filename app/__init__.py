from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.models import Base, engine
from app.routes import admin_auth, course_teacher


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model@app.on_event("startup")
    logger.info("Creating all tables")
    Base.metadata.create_all(engine)

    print("\n=== All Available Routes ===")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(route.methods)
            print(f"{methods:<10} {route.path}")
    print("========================\n")

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(admin_auth.router, prefix="/admin-auth", tags=["admin-auth"])
app.include_router(course_teacher.router, prefix="/course-teachers", tags=["course-teachers"])