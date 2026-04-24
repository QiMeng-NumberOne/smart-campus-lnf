from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import ok
from app.database import get_db
from app.models.user import User
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.item_repository import ItemRepository
from app.schemas.favorite import FavoriteCreate
from app.services.favorite_service import FavoriteService

router = APIRouter()


@router.post("")
def add(body: FavoriteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    FavoriteService(FavoriteRepository(db), ItemRepository(db)).add(user.id, body.item_id)
    return ok()


@router.delete("/{item_id}")
def remove(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    FavoriteService(FavoriteRepository(db), ItemRepository(db)).remove(user.id, item_id)
    return ok()


@router.get("")
def list_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = FavoriteService(FavoriteRepository(db), ItemRepository(db)).list(user.id)
    return ok(data)
