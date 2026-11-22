import csv
import io
import re
import unicodedata
from dataclasses import dataclass


EXPECTED_HEADER = [
    "department",
    "account_code",
    "description",
    "prior_year_amount",
    "proposed_amount",
]

_CURRENCY_RE = re.compile(r"-?[0-9]{1,12}(?:\.[0-9]{1,2})?\Z")
_MAX_ROWS = 5000
_MAX_BYTES = 1024 * 1024


@dataclass(frozen=True)
class BudgetLine:
    department: str
    account_code: str
    description: str
    prior_year_cents: int
    proposed_cents: int


@dataclass(frozen=True)
class BudgetCsvError:
    row: int
    reason: str


@dataclass(frozen=True)
class BudgetImport:
    lines: tuple[BudgetLine, ...]
    errors: tuple[BudgetCsvError, ...]

    @property
    def prior_year_total_cents(self) -> int:
        return sum(line.prior_year_cents for line in self.lines)

    @property
    def proposed_total_cents(self) -> int:
        return sum(line.proposed_cents for line in self.lines)


def _has_control_chars(value: str) -> bool:
    return any(unicodedata.category(ch) == "Cc" for ch in value)


def _parse_cents(value: str) -> int:
    negative = value.startswith("-")
    if negative:
        value = value[1:]

    if "." in value:
        whole, fraction = value.split(".", 1)
    else:
        whole, fraction = value, ""

    fraction = (fraction + "00")[:2]
    cents = int(whole) * 100 + int(fraction)
    return -cents if negative else cents


def parse_budget_csv(text: str) -> BudgetImport:
    try:
        size = len(text.encode("utf-8"))
    except UnicodeEncodeError as exc:
        return BudgetImport(
            (),
            (BudgetCsvError(1, f"input contains unencodable Unicode: {exc}"),),
        )

    if size > _MAX_BYTES:
        return BudgetImport((), (BudgetCsvError(0, "input exceeds 1 MiB"),))

    if text.startswith("\ufeff"):
        text = text[1:]

    reader = csv.reader(io.StringIO(text, newline=""), strict=True)

    header_line = reader.line_num + 1
    try:
        header = next(reader)
    except StopIteration:
        return BudgetImport((), (BudgetCsvError(1, "missing header"),))
    except csv.Error as exc:
        return BudgetImport((), (BudgetCsvError(header_line, f"csv error: {exc}"),))

    if header != EXPECTED_HEADER:
        return BudgetImport((), (BudgetCsvError(1, "invalid header"),))

    lines: list[BudgetLine] = []
    errors: list[BudgetCsvError] = []
    seen = set()
    data_row_count = 0

    while True:
        line_no = reader.line_num + 1
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error as exc:
            errors.append(BudgetCsvError(line_no, f"csv error: {exc}"))
            break

        data_row_count += 1
        if data_row_count > _MAX_ROWS:
            errors.append(BudgetCsvError(line_no, "more than 5000 data rows"))
            break

        if len(row) != 5:
            errors.append(
                BudgetCsvError(line_no, f"expected 5 fields, got {len(row)}")
            )
            continue

        department, account_code, description, prior_text, proposed_text = (
            field.strip() for field in row
        )

        row_ok = True

        text_fields = (
            ("department", department),
            ("account_code", account_code),
            ("description", description),
        )
        for name, value in text_fields:
            if not value:
                errors.append(BudgetCsvError(line_no, f"{name} is blank"))
                row_ok = False
            elif _has_control_chars(value):
                errors.append(
                    BudgetCsvError(line_no, f"{name} contains control characters")
                )
                row_ok = False

        if not _CURRENCY_RE.fullmatch(prior_text):
            errors.append(BudgetCsvError(line_no, "invalid prior_year_amount"))
            row_ok = False
            prior_cents = 0
        else:
            prior_cents = _parse_cents(prior_text)

        if not _CURRENCY_RE.fullmatch(proposed_text):
            errors.append(BudgetCsvError(line_no, "invalid proposed_amount"))
            row_ok = False
            proposed_cents = 0
        else:
            proposed_cents = _parse_cents(proposed_text)

        if not row_ok:
            continue

        key = (department.casefold(), account_code.casefold())
        if key in seen:
            errors.append(
                BudgetCsvError(line_no, "duplicate department/account_code")
            )
            continue
        seen.add(key)

        lines.append(
            BudgetLine(
                department=department,
                account_code=account_code,
                description=description,
                prior_year_cents=prior_cents,
                proposed_cents=proposed_cents,
            )
        )

    if errors:
        return BudgetImport((), tuple(errors))

    if not lines:
        return BudgetImport((), (BudgetCsvError(2, "no data rows"),))

    return BudgetImport(tuple(lines), ())
