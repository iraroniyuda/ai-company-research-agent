from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.company import Company


def get_all_companies(
    db: Session,
    industry: str | None = None,
    search: str | None = None,
):
    query = db.query(Company)

    if industry:
        query = query.filter(Company.industry == industry)

    if search:
        search_value = f"%{search}%"
        query = query.filter(
            or_(
                Company.company_name.ilike(search_value),
                Company.description.ilike(search_value),
                Company.industry.ilike(search_value),
                Company.summary.ilike(search_value),
            )
        )

    return query.all()


def get_company_by_id(db: Session, company_id: int):
    return db.query(Company).filter(Company.id == company_id).first()
