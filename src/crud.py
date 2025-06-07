# crud.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, extract
from src.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta
from typing import List, Optional


async def create_contact(db: AsyncSession, contact: ContactCreate) -> Contact:
    """
    Створює новий контакт у базі даних.
    """
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


async def get_contacts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Contact]:
    """
    Отримує список контактів з бази даних з можливістю пагінації.
    """
    result = await db.execute(select(Contact).offset(skip).limit(limit))
    return result.scalars().all()


async def get_contact(db: AsyncSession, contact_id: int) -> Optional[Contact]:
    """
    Отримує контакт за його ID.
    """
    result = await db.execute(select(Contact).filter(Contact.id == contact_id))
    return result.scalar_one_or_none()


async def update_contact(
    db: AsyncSession, contact_id: int, contact_data: ContactUpdate
) -> Optional[Contact]:
    """
    Оновлює контакт за його ID.
    """
    contact = await get_contact(db, contact_id)
    if contact:
        update_data = contact_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:  # Оновлюємо тільки поля з значеннями
                setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
        return contact
    return None


async def delete_contact(db: AsyncSession, contact_id: int) -> bool:
    """
    Видаляє контакт за його ID.
    """
    contact = await get_contact(db, contact_id)
    if contact:
        await db.delete(contact)
        await db.commit()
        return True
    return False


async def search_contacts(
    db: AsyncSession, query: str, skip: int = 0, limit: int = 100
) -> List[Contact]:
    """
    Шукає контакти за ключовими словами в імені, прізвищі або електронній пошті.    
    """
    result = await db.execute(
        select(Contact)
        .filter(
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def upcoming_birthdays(db: AsyncSession) -> List[Contact]:
    """
    Отримує контакти, у яких дні народження припадають на наступний тиждень.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    today_num = today.month * 100 + today.day
    next_week_num = next_week.month * 100 + next_week.day

    if next_week_num >= today_num:
        # Прямий діапазон
        stmt = select(Contact).filter(
            (
                extract("month", Contact.birthday) * 100
                + extract("day", Contact.birthday)
            ).between(today_num, next_week_num)
        )
    else:
        # Перехід через новий рік
        stmt = select(Contact).filter(
            or_(
                (
                    extract("month", Contact.birthday) * 100
                    + extract("day", Contact.birthday)
                )
                >= today_num,
                (
                    extract("month", Contact.birthday) * 100
                    + extract("day", Contact.birthday)
                )
                <= next_week_num,
            )
        )

    result = await db.execute(stmt)
    return result.scalars().all()