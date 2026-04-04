import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from app.core.database import SessionLocal, create_tables
from app.models.company import Company

SOURCE_URL = "https://www.ycombinator.com/companies/industry/api"
REQUEST_TIMEOUT = 20
MAX_COMPANIES = 10
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    )
}


def fetch_page_html() -> str:
    response = requests.get(
        SOURCE_URL,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def normalize_website(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None

    website = value.strip()
    if not website:
        return None

    if website.startswith("/"):
        return None

    if website.startswith(("http://", "https://")):
        return website

    return f"https://{website}"


def is_company_href(href: str | None) -> bool:
    if not href:
        return False
    return re.fullmatch(r"/companies/[^/?#]+", href) is not None


def extract_company_slug(href: str) -> str | None:
    match = re.fullmatch(r"/companies/([^/?#]+)", href)
    if match is None:
        return None
    slug = match.group(1).strip()
    return slug or None


def slug_to_company_name(slug: str | None) -> str | None:
    if not isinstance(slug, str):
        return None

    parts = [part for part in slug.strip().split("-") if part]
    if not parts:
        return None

    return " ".join(part.capitalize() for part in parts)


def clean_company_name(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None

    name = value.strip()
    if not name:
        return None

    # Buang pola umum YC / metadata
    name = re.sub(r"\bY\s*Combinator\s+Logo\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\b[A-Z]\d{4}\b", "", name)
    name = name.split("•", 1)[0]
    name = name.split("·", 1)[0]
    name = name.split("|", 1)[0]

    name = re.sub(r"\bActive\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\bInactive\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\bStealth\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\bPublic\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\bAcquired\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\b\d[\d,]*\+?\s+employees\b", "", name, flags=re.IGNORECASE)

    name = re.sub(r"\s+", " ", name).strip(" -|•·")
    if not name:
        return None

    if "y combinator logo" in name.lower():
        return None

    return name


def is_generic_description(text: str) -> bool:
    lowered = text.lower()
    generic_phrases = [
        "y combinator",
        "apply to yc",
        "batch",
        "companies built with",
        "view company",
    ]
    return any(phrase in lowered for phrase in generic_phrases)


def count_company_links(card: Tag) -> int:
    count = 0
    for link in card.find_all("a", href=True):
        href = link.get("href", "").strip()
        if is_company_href(href):
            count += 1
    return count


def find_company_card(company_link: Tag) -> Tag | None:
    current: Tag | None = company_link

    while current is not None:
        if current.name in {"div", "li", "article", "section"}:
            if count_company_links(current) == 1:
                return current
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None

    return None


def extract_company_name(card: Tag, company_link: Tag, slug: str | None = None) -> str | None:
    candidates: list[str] = []

    for heading in card.find_all(["h1", "h2", "h3", "h4"]):
        text = heading.get_text(" ", strip=True)
        if text:
            candidates.append(text)

    link_text = company_link.get_text(" ", strip=True)
    if link_text:
        candidates.append(link_text)

    image = card.find("img", alt=True)
    if image is not None:
        alt = image.get("alt", "").strip()
        cleaned_alt = clean_company_name(alt)
        if cleaned_alt:
            candidates.append(alt)

    cleaned_candidates: list[str] = []
    for candidate in candidates:
        cleaned = clean_company_name(candidate)
        if cleaned:
            cleaned_candidates.append(cleaned)

    if cleaned_candidates:
        reasonable_candidates = [candidate for candidate in cleaned_candidates if len(candidate) <= 80]
        if reasonable_candidates:
            return min(reasonable_candidates, key=len)
        return min(cleaned_candidates, key=len)

    return slug_to_company_name(slug)


def extract_description(card: Tag, company_link: Tag) -> str | None:
    link_text = company_link.get_text(" ", strip=True)

    for tag in card.find_all(["p", "div", "span"]):
        text = tag.get_text(" ", strip=True)
        if not text or text == link_text:
            continue
        if len(text) < 25:
            continue
        if "•" in text:
            continue
        if is_generic_description(text):
            continue
        return text

    return None


def extract_website(card: Tag) -> str | None:
    external_links: list[str] = []

    for link in card.find_all("a", href=True):
        href = link.get("href", "").strip()
        parsed = urlparse(href)

        if parsed.scheme not in {"http", "https"}:
            continue
        if "ycombinator.com" in parsed.netloc:
            continue

        external_links.append(href)

    if not external_links:
        return None

    return normalize_website(external_links[0])


def choose_better_candidate(current: dict, candidate: dict) -> dict:
    current_has_website = current.get("website") is not None
    candidate_has_website = candidate.get("website") is not None

    if candidate_has_website and not current_has_website:
        return candidate
    if current_has_website and not candidate_has_website:
        return current

    current_description = current["description"]
    candidate_description = candidate["description"]

    if len(candidate_description) > len(current_description):
        return candidate
    if len(current_description) > len(candidate_description):
        return current

    return current


def collect_from_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    companies_by_slug: dict[str, dict] = {}

    for company_link in soup.find_all("a", href=True):
        href = company_link.get("href", "").strip()
        if not is_company_href(href):
            continue

        slug = extract_company_slug(href)
        if not slug:
            continue

        card = find_company_card(company_link)
        if card is None:
            continue

        company_name = extract_company_name(card, company_link, slug)
        description = extract_description(card, company_link)

        if not company_name or not description:
            continue

        cleaned_name = clean_company_name(company_name)
        if not cleaned_name:
            continue

        candidate = {
            "slug": slug,
            "company_name": cleaned_name,
            "website": extract_website(card),
            "description": description,
        }

        existing = companies_by_slug.get(slug)
        if existing is None:
            companies_by_slug[slug] = candidate
        else:
            companies_by_slug[slug] = choose_better_candidate(existing, candidate)

        if len(companies_by_slug) >= MAX_COMPANIES:
            break

    return [
        {
            "company_name": company["company_name"],
            "website": company["website"],
            "description": company["description"],
        }
        for company in list(companies_by_slug.values())[:MAX_COMPANIES]
    ]


def collect_companies() -> list[dict]:
    html = fetch_page_html()
    return collect_from_html(html)


def main() -> None:
    create_tables()
    db = SessionLocal()
    fetched = 0
    inserted = 0
    skipped = 0

    try:
        companies = collect_companies()
        fetched = len(companies)

        for company_data in companies:
            company_name = company_data["company_name"]
            description = company_data["description"]

            if not company_name or not description:
                skipped += 1
                continue

            existing_company = (
                db.query(Company)
                .filter(Company.company_name == company_name)
                .first()
            )
            if existing_company is not None:
                skipped += 1
                continue

            company = Company(
                company_name=company_name,
                website=company_data["website"],
                description=description,
                industry=None,
                business_model=None,
                summary=None,
                use_case=None,
            )
            db.add(company)
            inserted += 1

        db.commit()
    finally:
        db.close()

    print(f"fetched {fetched}")
    print(f"inserted {inserted}")
    print(f"skipped {skipped}")


if __name__ == "__main__":
    main()