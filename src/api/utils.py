from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database.db import get_db

router = APIRouter(tags=["utils"])

# Перевірка стану API
@router.get(
    "/healthchecker",
    summary="Перевірка стану API",
    description="Перевіряє з'єднання з базою даних.",
)
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Виконуємо асинхронний запит
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
