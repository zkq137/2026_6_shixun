from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.models  # noqa: F401
from sqlalchemy import inspect, text

from app.core.database import SessionLocal, engine
from app.models import Admin, Category, Faq, Product, ProductReview, SalesStatistic, UserBehavior


def count(session, model) -> int:
    return session.query(model).count()


def main():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with SessionLocal() as session:
        print("Database connection: ok")
        print(f"Table count: {len(tables)}")
        print(f"admins: {count(session, Admin)}")
        print(f"categories: {count(session, Category)}")
        print(f"products: {count(session, Product)}")
        print(f"product_reviews: {count(session, ProductReview)}")
        print(f"faqs: {count(session, Faq)}")
        print(f"user_behaviors: {count(session, UserBehavior)}")
        print(f"sales_statistics: {count(session, SalesStatistic)}")


if __name__ == "__main__":
    main()
