from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from src.database import get_db
from src.models import Base  # таблиці створюються через Alembic
from src import crud, schemas

app = FastAPI(
    title="Contacts API",
    description="REST API для управління контактами",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Контакт з такою електронною адресою вже існує"},
    )


@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=201)
async def create_contact(
    contact: schemas.ContactCreate, db: AsyncSession = Depends(get_db)
):
    return await crud.create_contact(db=db, contact=contact)


@app.get("/contacts/", response_model=List[schemas.ContactResponse])
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    if search:
        return await crud.search_contacts(db=db, query=search, skip=skip, limit=limit)
    return await crud.get_contacts(db=db, skip=skip, limit=limit)


@app.get("/contacts/upcoming-birthdays/", response_model=List[schemas.ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await crud.upcoming_birthdays(db)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    db_contact = await crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    return db_contact


@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: schemas.ContactUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_contact = await crud.update_contact(
        db, contact_id=contact_id, contact_data=contact_update
    )
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    return updated_contact


@app.delete("/contacts/{contact_id}", status_code=204)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_contact(db, contact_id=contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")


@app.get("/")
async def root():
    return {"message": "Contacts API", "docs": "/docs", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)