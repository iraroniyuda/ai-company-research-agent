from app.core.database import SessionLocal, create_tables
from app.models.company import Company


SAMPLE_COMPANIES = [
    {
        "company_name": "OpenAI",
        "website": "https://openai.com",
        "description": "AI research and deployment company building language and multimodal models.",
    },
    {
        "company_name": "Stripe",
        "website": "https://stripe.com",
        "description": "Financial infrastructure platform for online payments and internet businesses.",
    },
    {
        "company_name": "Notion",
        "website": "https://www.notion.so",
        "description": "Workspace software for notes, documents, wikis, and project collaboration.",
    },
    {
        "company_name": "Canva",
        "website": "https://www.canva.com",
        "description": "Online design platform for presentations, social media graphics, and marketing assets.",
    },
    {
        "company_name": "Figma",
        "website": "https://www.figma.com",
        "description": "Collaborative interface design and product development platform.",
    },
    {
        "company_name": "Datadog",
        "website": "https://www.datadoghq.com",
        "description": "Cloud monitoring and observability platform for infrastructure and applications.",
    },
    {
        "company_name": "Airtable",
        "website": "https://www.airtable.com",
        "description": "Flexible database and workflow platform for teams managing structured information.",
    },
    {
        "company_name": "Scale AI",
        "website": "https://scale.com",
        "description": "Data platform supporting AI model training, evaluation, and deployment workflows.",
    },
    {
        "company_name": "Anthropic",
        "website": None,
        "description": "AI safety and research company developing large language models and assistants.",
    },
    {
        "company_name": "Mistral AI",
        "website": None,
        "description": "AI company building foundation models and related developer products.",
    },
]


def main():
    create_tables()
    db = SessionLocal()
    inserted = 0
    skipped = 0

    try:
        for company_data in SAMPLE_COMPANIES:
            existing_company = (
                db.query(Company)
                .filter(Company.company_name == company_data["company_name"])
                .first()
            )
            if existing_company is not None:
                skipped += 1
                continue

            company = Company(
                company_name=company_data["company_name"],
                website=company_data["website"],
                description=company_data["description"],
                industry=None,
                business_model=None,
                summary=None,
                use_case=None,
            )
            db.add(company)
            inserted += 1

        db.commit()
        print(f"Inserted {inserted}, skipped {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
