from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

import sqlalchemy as sa

from .budget_import import BudgetImport

__all__ = ["budget_revisions", "metadata", "ensure_budget_schema", "revision_content"]

metadata = sa.MetaData(schema="townlight_budget")

budget_revisions = sa.Table(
    "budget_revisions",
    metadata,
    sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
    sa.Column("fiscal_year", sa.Integer, nullable=False),
    sa.Column("imported_by", sa.Uuid(as_uuid=True), nullable=False),
    sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("content_sha256", sa.String(64), nullable=False),
    sa.Column("lines", sa.JSON, nullable=False),
    sa.Column("prior_year_total_cents", sa.BigInteger, nullable=False),
    sa.Column("proposed_total_cents", sa.BigInteger, nullable=False),
    sa.Column("finance_reviewed_by", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("finance_reviewed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("hearing_meeting_id", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("hearing_agenda_id", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("packet_id", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("packet_approval_id", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("packet_manifest_sha256", sa.String(64), nullable=True),
    sa.Column("adopted_by", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("adopted_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("recorded_motion_id", sa.Uuid(as_uuid=True), nullable=True),
    sa.Column("recorded_vote_ids", sa.JSON, nullable=True),
    sa.Column("reviewed_public_summary", sa.Text, nullable=True),
)


def ensure_budget_schema(engine: sa.Engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            sa.schema.CreateSchema("townlight_budget", if_not_exists=True)
        )
        metadata.create_all(conn)


def revision_content(fiscal_year: int, parsed: BudgetImport) -> tuple[dict, str]:
    if parsed.errors or not parsed.lines:
        raise ValueError("budget import has errors or no lines")

    payload = {
        "fiscal_year": fiscal_year,
        "prior_year_total_cents": parsed.prior_year_total_cents,
        "proposed_total_cents": parsed.proposed_total_cents,
        "lines": [asdict(line) for line in parsed.lines],
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload, digest
