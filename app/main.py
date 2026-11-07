from fastapi import FastAPI
from app.database import Base, engine
from app.routers import router
from app import models


app = FastAPI(
    title="Person Service",
    description="REST API для управления пользователями",
    version="1.0.0",
)

app.include_router(router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Person Service is running"}
