"""
Score articles by keyword relevance using config/topics.yaml rules.

Scoring:
  - Company keyword match  → +3 points per match
  - Category keyword match → +1 point per match

Articles below min_relevance_score are dropped.
Results are sorted by score descending and capped at max_articles.
"""

import logging

logger = logging.getLogger(__name__)


def score_articles(
    articles: list[dict],
    topics_config: dict,
    min_relevance_score: int = 2,
    max_articles: int = 25,
) -> list[dict]:
    """Score, filter, and rank articles for relevance."""

    # Build (lowercase keyword, label) lookup tables
    company_kws: list[tuple[str, str]] = []  # (keyword, company name)
    category_kws: list[tuple[str, str]] = []  # (keyword, category name)

    for _group, companies in topics_config.get("companies_to_track", {}).items():
        if not isinstance(companies, list):
            continue
        for company in companies:
            name = company.get("name", "")
            for kw in company.get("keywords", []):
                company_kws.append((kw.lower(), name))

    for cat in topics_config.get("topic_categories", []):
        cat_name = cat.get("name", "")
        for kw in cat.get("keywords", []):
            category_kws.append((kw.lower(), cat_name))

    scored: list[dict] = []

    for article in articles:
        text = (
            article.get("title", "") + " " + article.get("summary", "")
        ).lower()

        score = 0
        companies: list[str] = []
        categories: list[str] = []
        keywords: list[str] = []

        for kw, company in company_kws:
            if kw in text:
                score += 3
                if company not in companies:
                    companies.append(company)
                if kw not in keywords:
                    keywords.append(kw)

        for kw, category in category_kws:
            if kw in text:
                score += 1
                if category not in categories:
                    categories.append(category)

        article["relevance_score"] = score
        article["matched_companies"] = companies
        article["matched_categories"] = categories
        article["matched_keywords"] = keywords

        if score >= min_relevance_score:
            scored.append(article)

    scored.sort(key=lambda a: a["relevance_score"], reverse=True)
    return scored[:max_articles]
