from townlight_budget.budget_import import parse_budget_csv


def test_exact_totals_and_preserved_zero_account_with_bom_and_quoted_fields():
    text = (
        "\ufeffdepartment,account_code,description,prior_year_amount,proposed_amount\n"
        '"Public Works","000123","Road, salt",12.34,0.00\n'
        'Parks,"0000","Trees",0.01,100.00\n'
    )

    result = parse_budget_csv(text)

    assert result.errors == ()
    assert len(result.lines) == 2

    first, second = result.lines

    assert first.department == "Public Works"
    assert first.account_code == "000123"
    assert first.description == "Road, salt"
    assert first.prior_year_cents == 1234
    assert first.proposed_cents == 0

    assert second.department == "Parks"
    assert second.account_code == "0000"
    assert second.description == "Trees"
    assert second.prior_year_cents == 1
    assert second.proposed_cents == 10000

    assert result.prior_year_total_cents == 1235
    assert result.proposed_total_cents == 10000


def test_whole_batch_rejects_currency_rounding_malformed_decimal_and_duplicate_rows():
    text = (
        "department,account_code,description,prior_year_amount,proposed_amount\n"
        "Engineering,E100,Good row,10.00,20.00\n"
        "Ops,O1,Currency rounding,1.005,2.00\n"
        "Sales,S1,Malformed decimal,abc,3.00\n"
        "Eng,DUP,Duplicate,4.00,5.00\n"
        "Eng,DUP,Duplicate,4.00,5.00\n"
    )

    result = parse_budget_csv(text)

    assert result.lines == ()
    assert [error.row for error in result.errors] == [3, 4, 6]


def test_malformed_csv_syntax_reports_line_and_saves_nothing():
    text = (
        "department,account_code,description,prior_year_amount,proposed_amount\n"
        'A,A1,"unterminated,1.00,2.00\n'
    )

    result = parse_budget_csv(text)

    assert result.lines == ()
    assert len(result.errors) == 1
    assert result.errors[0].row == 2
