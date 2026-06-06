from __future__ import annotations

import argparse

from market_copilot.db.models import SourceDocument
from market_copilot.db.session import SessionLocal
from market_copilot.ingestion.congressional.persistence import create_normalization_jobs_for_documents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Queue normalization jobs again for one or more congressional source records."
    )
    parser.add_argument(
        "source_record_ids",
        nargs="+",
        help="House PTR source_record_id values to requeue",
    )
    args = parser.parse_args()

    with SessionLocal() as session:
        documents = (
            session.query(SourceDocument)
            .filter(SourceDocument.document_type == "ptr_pdf")
            .filter(SourceDocument.source_record_id.in_(args.source_record_ids))
            .all()
        )

        if not documents:
            print(
                {
                    "status": "no_matching_documents",
                    "source_record_ids": args.source_record_ids,
                }
            )
            return

        jobs = create_normalization_jobs_for_documents(
            session=session,
            documents=documents,
        )
        session.commit()

        print(
            {
                "status": "queued",
                "source_record_ids": sorted(
                    {
                        document.source_record_id
                        for document in documents
                        if document.source_record_id
                    }
                ),
                "jobs_created": len(jobs),
            }
        )


if __name__ == "__main__":
    main()
