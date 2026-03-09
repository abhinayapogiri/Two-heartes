from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_db
from models.theatre import Theatre

class TheatreResponse(BaseModel):
    id: int
    name: str
    city: str
    owner_id: int

router = APIRouter(prefix="", tags=["Public"])

@router.get("/locations", response_model=List[str])
def get_locations(db: Session = Depends(get_db)):
    """
    Get list of unique cities where theatres exist.
    """
    cities = db.query(func.trim(Theatre.city)).distinct().all()
    # cities is a list of Row objects, e.g. [('Visakhapatnam',), ('Vijayawada',)]
    # Use sorted and filtered list
    return sorted(list(set(city[0] for city in cities if city[0])))

@router.get("/theatres", response_model=List[TheatreResponse])
def get_theatres(
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all theatres, optionally filtered by city.
    """
    query = db.query(Theatre)
    if city:
        city_clean = city.strip().lower()
        query = query.filter(func.lower(func.trim(Theatre.city)) == city_clean)
    
    return query.all()
