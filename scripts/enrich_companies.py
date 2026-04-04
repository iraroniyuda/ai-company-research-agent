from app.core.database import SessionLocal, create_tables
from app.models.analysis_cache import AnalysisCache
from app.models.company import Company
from app.services.analyzer import CompanyAnalysis, analyze_company_description


def needs_enrichment(company: Company) -> bool:
    return any(
        value is None
        for value in (
            company.industry,
            company.business_model,
            company.summary,
            company.use_case,
        )
    )


def is_empty_analysis(analysis) -> bool:
    return all(
        value is None
        for value in (
            analysis.industry,
            analysis.business_model,
            analysis.summary,
            analysis.use_case,
        )
    )


def get_cached_analysis(db, description: str) -> CompanyAnalysis | None:
    cached = (
        db.query(AnalysisCache)
        .filter(AnalysisCache.description == description)
        .first()
    )
    if cached is None:
        return None

    return CompanyAnalysis(
        industry=cached.industry,
        business_model=cached.business_model,
        summary=cached.summary,
        use_case=cached.use_case,
    )


def store_analysis_cache(db, description: str, analysis: CompanyAnalysis) -> None:
    if is_empty_analysis(analysis):
        return

    existing = (
        db.query(AnalysisCache)
        .filter(AnalysisCache.description == description)
        .first()
    )
    if existing is not None:
        return

    db.add(
        AnalysisCache(
            description=description,
            industry=analysis.industry,
            business_model=analysis.business_model,
            summary=analysis.summary,
            use_case=analysis.use_case,
        )
    )
    db.flush()


def main():
    create_tables()
    db = SessionLocal()
    processed = 0
    updated = 0
    skipped = 0

    try:
        companies = db.query(Company).all()

        for company in companies:
            if not needs_enrichment(company):
                skipped += 1
                continue

            processed += 1
            analysis = get_cached_analysis(db, company.description)
            if analysis is None:
                analysis = analyze_company_description(company.description)

            if is_empty_analysis(analysis):
                skipped += 1
                continue

            company.industry = analysis.industry
            company.business_model = analysis.business_model
            company.summary = analysis.summary
            company.use_case = analysis.use_case

            try:
                store_analysis_cache(db, company.description, analysis)
                db.commit()
                updated += 1
            except Exception:
                db.rollback()
    finally:
        db.close()

    print(f"processed {processed}")
    print(f"updated {updated}")
    print(f"skipped {skipped}")


if __name__ == "__main__":
    main()
