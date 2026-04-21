# 贡献CRUD操作
from sqlmodel import Session, select

from app.models.user import UserContribution


def get_contribution(db: Session, contribution_id: int):
    return db.exec(select(UserContribution).where(UserContribution.id == contribution_id)).first()

def get_contributions(db: Session, skip: int = 0, limit: int = 100):
    return db.exec(select(UserContribution).offset(skip).limit(limit)).all()

def create_contribution(db: Session, contribution):
    db_contribution = UserContribution(**contribution.dict())
    db.add(db_contribution)
    db.commit()
    db.refresh(db_contribution)
    return db_contribution