from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import ok
from app.database import get_db
from app.models.user import User
from app.schemas.ai import RecognizeItemRequest, ApplySuggestionRequest, RecognizeImageRequest
from app.schemas.id_card import IdCardOcrRequest
from app.services.ai_service import AIService

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    return ok(AIService(db).health())


@router.post("/recognize/item/{item_id}")
def recognize_item(
    item_id: int,
    body: RecognizeItemRequest,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data, err = AIService(db).recognize_item(item_id=item_id, image_id=body.image_id, conf_threshold=body.conf_threshold)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)


@router.post("/recognize/image")
def recognize_image(
    body: RecognizeImageRequest,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data, err = AIService(db).recognize_image_url(image_url=body.image_url, conf_threshold=body.conf_threshold)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)


@router.post("/ocr/id-card")
def ocr_id_card(
    body: IdCardOcrRequest,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = AIService(db).recognize_id_card_text(body.image_url)
    return ok(data)


@router.post("/apply-suggestion")
def apply_suggestion(
    body: ApplySuggestionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data, err = AIService(db).apply_suggestion(user_id=user.id, item_id=body.item_id, item_type_id=body.item_type_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)
