from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    company_name: str
    website: str | None = None
    description: str
    industry: str | None = None
    business_model: str | None = None
    summary: str | None = None
    use_case: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
