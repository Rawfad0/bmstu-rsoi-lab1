from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import PersonRequest, PersonResponse, PersonUpdate

router = APIRouter(prefix="/api/v1/persons", tags=["persons"])


def person_not_found():
    return JSONResponse(
        status_code=404,
        content={"message": "Person not found"},
    )


@router.get("", response_model=list[PersonResponse])
def get_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@router.get("/{personId}", response_model=PersonResponse)
def get_person(personId: int, db: Session = Depends(get_db)):
    person = db.get(models.Person, personId)

    if person is None:
        return person_not_found()

    return person


@router.post("", status_code=201)
def create_person(
    person_data: PersonRequest,
    db: Session = Depends(get_db),
):
    person = models.Person(
        name=person_data.name,
        age=person_data.age,
        address=person_data.address,
        work=person_data.work,
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    return Response(
        status_code=201,
        headers={"Location": f"/api/v1/persons/{person.id}"},
    )


@router.patch("/{personId}", response_model=PersonResponse)
def update_person(
    personId: int,
    person_data: PersonUpdate,
    db: Session = Depends(get_db),
):
    person = db.get(models.Person, personId)

    if person is None:
        return person_not_found()

    update_data = person_data.model_dump(exclude_unset=True)

    if not update_data:
        return JSONResponse(
            status_code=400,
            content={"message": "No fields to update"},
        )

    for field, value in update_data.items():
        setattr(person, field, value)

    db.commit()
    db.refresh(person)

    return person


@router.delete("/{personId}", status_code=204)
def delete_person(
    personId: int,
    db: Session = Depends(get_db),
):
    person = db.get(models.Person, personId)

    if person is None:
        return person_not_found()

    db.delete(person)
    db.commit()

    return Response(status_code=204)
