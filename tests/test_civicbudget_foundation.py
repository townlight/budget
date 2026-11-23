from townlight_budget import __version__
from townlight_budget.gfoa_review import review_gfoa_alignment
from townlight_budget.hearing_packet import build_hearing_packet_checklist
from townlight_budget.line_item_analysis import analyze_line_items
from townlight_budget.memo import draft_budget_memo
from townlight_budget.narrative import draft_budget_narrative
from townlight_budget.resident_summary import draft_resident_summary


def test_version_is_release_version():
    assert __version__ == "0.2.0"


def test_line_item_analysis_flags_material_variance():
    variance = analyze_line_items(
        [{"account": "101", "current_amount": 150000, "prior_amount": 100000}]
    )[0]

    assert variance.variance == 50000
    assert "Material" in variance.review_note or "Finance review" in variance.review_note


def test_narrative_requires_finance_review():
    assert draft_budget_narrative("Parks", ["Maintain fields"], []).requires_finance_review is True


def test_memo_is_not_approval():
    assert draft_budget_memo("Finance", "Council", ["Balanced budget"]).not_a_approval is True


def test_hearing_packet_requires_clerk_handoff():
    assert build_hearing_packet_checklist("FY27", ["Budget memo"]).clerk_handoff_required is True


def test_resident_summary_requires_publication_review():
    assert draft_resident_summary(
        "General fund",
        ["Revenue up 2%"],
    ).requires_publication_review is True


def test_gfoa_review_is_checklist_not_certification():
    assert "does not certify" in review_gfoa_alignment(True).boundary
