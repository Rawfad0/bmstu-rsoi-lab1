from pydantic import BaseModel


class PersonRequest(BaseModel):
    name: str
    age: int | None = None
    address: str | None = None
    work: str | None = None


class PersonUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    address: str | None = None
    work: str | None = None


class PersonResponse(BaseModel):
    id: int
    name: str
    age: int | None = None
    address: str | None = None
    work: str | None = None


class ErrorResponse(BaseModel):
    message: str
