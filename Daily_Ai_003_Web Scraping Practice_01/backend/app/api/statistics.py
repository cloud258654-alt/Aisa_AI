from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.statistics_service import get_statistics

router = APIRouter(tags=["statistics"])


@router.get("/statistics")
async def statistics(db: Session = Depends(get_db)):
    return get_statistics(db)
