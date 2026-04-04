from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.company import CompanyResponse
from app.services.repository import get_all_companies, get_company_by_id

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    db: Annotated[Session, Depends(get_db)],
    industry: str | None = None,
    search: str | None = None,
):
    return get_all_companies(db, industry=industry, search=search)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Annotated[Session, Depends(get_db)]):
    company = get_company_by_id(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
