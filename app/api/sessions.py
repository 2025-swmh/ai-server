from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Session as SessionModel
from app.schemas import SessionCreate

router = APIRouter()


@router.post("/template", status_code=status.HTTP_201_CREATED)
async def save_template(session_data: SessionCreate, db: Session = Depends(get_db)) -> str:

    if db.query(SessionModel).filter(SessionModel.session_id == session_data.session_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 템플릿을 지정하셨습니다.")

    new_session = SessionModel(session_id=session_data.session_id, template=session_data.template)
    db.add(new_session)
    db.commit()

    return "템플릿이 정상적으로 저장되었습니다."
