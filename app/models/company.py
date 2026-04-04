from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str | None] = mapped_column(String, nullable=True)
    business_model: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    use_case: Mapped[str | None] = mapped_column(Text, nullable=True)
