from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from core.database import get_db
from models.movie import Movie
from schemas.movie import MovieResponse

router = APIRouter(prefix="/movies", tags=["Movies"])


from api import deps
from models.user import User

from typing import List, Optional
from models.show import Show
from models.screen import Screen
from models.theatre import Theatre

@router.get("", response_model=List[MovieResponse])
def list_movies(
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all movies, optionally filtered by city where they are showing.
    """
    query = db.query(Movie)
    
    if city:
        city_clean = city.strip().lower()
        # Join with Show, Screen, and Theatre to filter by city
        query = query.join(Show, Movie.id == Show.movie_id)\
                     .join(Screen, Show.screen_id == Screen.id)\
                     .join(Theatre, Screen.theatre_id == Theatre.id)\
                     .filter(func.lower(func.trim(Theatre.city)) == city_clean)\
                     .distinct()
    
    movies = query.all()
    
    # Enrich with technologies
    for movie in movies:
        techs = db.query(Screen.technology)\
                  .join(Show, Screen.id == Show.screen_id)\
                  .filter(Show.movie_id == movie.id)\
                  .distinct().all()
        movie.available_technologies = [t[0] for t in techs if t[0]]
    
    return movies


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )
    
    techs = db.query(Screen.technology)\
              .join(Show, Screen.id == Show.screen_id)\
              .filter(Show.movie_id == movie.id)\
              .distinct().all()
    movie.available_technologies = [t[0] for t in techs if t[0]]

    return movie

