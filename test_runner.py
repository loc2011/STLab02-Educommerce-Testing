"""CSV-driven test execution for the EduCommerce STLab02 assignment.

The runner never rewrites expected values in test_cases.csv. Each row receives
its own fixture; actual results are written to reports/test_execution.csv.
Only Python standard-library modules are required.
"""
from __future__ import annotations

import csv
import json
import time
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
from pathlib import Path
from typing import Any

from ecommerce_app import D, fixture

ROOT = Path(__file__).resolve().parent
REQUIRED_COLUMNS = {
    "test_case_id", "requirement_id", "condition_id", "scenario_id", "title",
    "priority", "precondition", "fixture_key", "input_json", "expected_type",
    "expected_json", "execution_status", "actual_result", "error_message",
    "evidence_reference",
}


def _load_json(value: str, field: str, row_id: str) -> dict:
    if value is None or not str(value).strip():
        raise ValueError(f"{row_id}: {field} is empty")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{row_id}: invalid {field}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{row_id}: {field} must be a JSON object")
    return parsed


def load_cases(csv_path: str | Path) -> list[dict[str, str]]:
    path = Path(csv_path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("MALFORMED_CSV_ROW: row has an unexpected number of columns")
    ids = [row["test_case_id"].strip() for row in rows]
    if not rows:
        raise ValueError("CSV contains no test cases")
    if any(not case_id for case_id in ids):
        raise ValueError("EMPTY_TEST_CASE_ID")
    duplicates = sorted(case_id for case_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"DUPLICATE_TEST_IDS: {duplicates}")
    return rows


def _snapshot(app, customer) -> dict[str, Any]:
    return {
        "stock": {sku: product.stock for sku, product in app.catalog.products.items()},
        "order_count": len(app.orders),
        "charge_count": len(app.payments.charges),
        "used_codes": sorted(customer.used_codes),
    }


def _subset_matches(actual: dict, expected: dict) -> bool:
    """Compare only explicit expected keys; nested dicts are subset-matched."""
    for key, expected_value in expected.items():
        if key not in actual:
            return False
        actual_value = actual[key]
        if isinstance(expected_value, dict):
            if not isinstance(actual_value, dict) or not _subset_matches(actual_value, expected_value):
                return False
        elif actual_value != expected_value:
            return False
    return True


def execute_case(row: dict[str, str]) -> dict[str, Any]:
    case_id = row["test_case_id"].strip()
    started = time.perf_counter()
    evidence_ref = f"EV-{case_id}"
    app = customer = cart = None
    error_message = ""
    exception_type = ""
    result: dict[str, Any] = {}
    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    state_notes: list[str] = []
    inputs: dict[str, Any] = {}
    expected: dict[str, Any] = {}
    preparation_error = ""

    # Stage 1: parse and validate the test data / precondition.
    try:
        inputs = _load_json(row["input_json"], "input_json", case_id)
        expected = _load_json(row["expected_json"], "expected_json", case_id)
        app, customer, cart = fixture(
            row["fixture_key"].strip(),
            inputs.get("fixture_config", {}),
        )
        before = _snapshot(app, customer)
    except Exception as exc:
        preparation_error = f"TEST_DATA_OR_SETUP_ERROR: {type(exc).__name__}: {exc}"

    # Stage 2: dispatch the operation. Expected exceptions are compared below;
    # unexpected exceptions become FAIL, while invalid setup remains BLOCKED.
    if not preparation_error:
        try:
            operation = inputs.get("operation", "")
            if operation == "catalog_get":
                product = app.catalog.get(inputs.get("sku", ""))
                result = {"sku": product.sku, "active": product.active, "price": str(product.price)}
            elif operation == "cart_add":
                cart.add(inputs["sku"], inputs["quantity"])
                result = {
                    "lines": [{"sku": line.sku, "quantity": line.quantity} for line in cart.lines],
                    "subtotal": str(cart.subtotal()),
                    "subtotal_type": type(cart.subtotal()).__name__,
                }
            elif operation == "cart_subtotal":
                subtotal = cart.subtotal()
                result = {"subtotal": str(subtotal), "subtotal_type": type(subtotal).__name__}
            elif operation == "shipping_calculate":
                fee = app.shipping.calculate(D(inputs["subtotal"]), inputs["area"])
                result = {"shipping_fee": str(fee), "fee_type": type(fee).__name__}
            elif operation == "checkout":
                order = app.place(
                    customer,
                    cart,
                    area=inputs.get("area", "inner"),
                    voucher=inputs.get("voucher"),
                    method=inputs.get("method", "COD"),
                    approved=inputs.get("approved", True),
                    key=inputs.get("key", case_id),
                )
                result = {
                    "order_id": order.order_id,
                    "customer_id": order.customer_id,
                    "status": order.status,
                    "total": str(order.total),
                    "discount": str(order.discount),
                    "shipping": str(order.shipping),
                    "payment_method": order.payment_method,
                    "lines": [{"sku": sku, "quantity": quantity} for sku, quantity in order.lines],
                    "order_count": len(app.orders),
                    "charge_count": len(app.payments.charges),
                }
            else:
                raise RuntimeError(f"UNKNOWN_TEST_OPERATION: {operation}")
        except Exception as exc:
            exception_type = type(exc).__name__
            error_message = str(exc)
            result = {"exception_type": exception_type, "error": error_message}

    if app is not None and customer is not None:
        after = _snapshot(app, customer)
        if before and before["stock"] != after["stock"]:
            state_notes.append("stock changed")
        if before and before["order_count"] != after["order_count"]:
            state_notes.append("order count changed")
        if before and before["charge_count"] != after["charge_count"]:
            state_notes.append("payment charge count changed")
        if before and before["used_codes"] != after["used_codes"]:
            state_notes.append("used voucher state changed")

    if preparation_error:
        status = "BLOCKED"
        error_message = preparation_error
    elif row["expected_type"].strip() == "exception":
        expected_error = expected.get("exception", "")
        passed = exception_type == "ValueError" and error_message == expected_error
        if passed and "assert_state" in expected:
            actual_state = {
                "order_count": after.get("order_count"),
                "charge_count": after.get("charge_count"),
                "used_codes": after.get("used_codes"),
            }
            passed = _subset_matches(actual_state, expected["assert_state"])
        status = "PASS" if passed else "FAIL"
    elif row["expected_type"].strip() == "result":
        passed = not exception_type and _subset_matches(result, expected)
        status = "PASS" if passed else "FAIL"
    else:
        status = "FAIL"
        error_message = error_message or f"UNKNOWN_EXPECTED_TYPE: {row['expected_type']}"

    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    actual_blob = {
        "result": result,
        "exception_type": exception_type,
        "before": before,
        "after": after,
        "state_notes": state_notes,
    }
    return {
        "test_case_id": case_id,
        "requirement_id": row["requirement_id"],
        "condition_id": row["condition_id"],
        "scenario_id": row["scenario_id"],
        "title": row["title"],
        "priority": row["priority"],
        "expected_type": row["expected_type"],
        "expected_json": row["expected_json"],
        "actual_result": json.dumps(actual_blob, ensure_ascii=False, sort_keys=True),
        "error_message": error_message,
        "status": status,
        "execution_time_ms": duration_ms,
        "executed_at": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds"),
        "evidence_reference": evidence_ref,
        "state_observation": "; ".join(state_notes) if state_notes else "no unexpected state change observed",
    }


def write_reports(results: list[dict[str, Any]], out_dir: str | Path) -> dict[str, Path]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "test_execution.csv"
    fields = list(results[0].keys())
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    status_counts = Counter(row["status"] for row in results)
    by_requirement: dict[str, Counter] = defaultdict(Counter)
    for row in results:
        by_requirement[row["requirement_id"]][row["status"]] += 1
    total = len(results)
    passed = status_counts["PASS"]
    failed = status_counts["FAIL"]
    blocked = status_counts["BLOCKED"]
    pass_rate = (passed / total * 100) if total else 0.0

    summary_rows = []
    for req_id in sorted(by_requirement):
        c = by_requirement[req_id]
        summary_rows.append((req_id, c["PASS"], c["FAIL"], c["BLOCKED"], sum(c.values())))

    table_rows = "".join(
        "<tr>" + "".join(
            f"<td>{escape(str(row[key]))}</td>" for key in
            ("test_case_id", "requirement_id", "scenario_id", "expected_json", "actual_result", "status", "execution_time_ms")
        ) + "</tr>"
        for row in results
    )
    req_rows = "".join(
        f"<tr><td>{escape(req)}</td><td>{p}</td><td>{f}</td><td>{b}</td><td>{n}</td></tr>"
        for req, p, f, b, n in summary_rows
    )
    chart_total = max(total, 1)
    pass_width = passed / chart_total * 100
    fail_width = failed / chart_total * 100
    blocked_width = blocked / chart_total * 100
    html_page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>EduCommerce - Test Execution Report</title>
<style>
body{{font-family:Arial,sans-serif;margin:28px;color:#203040;background:#f7f9fb}}
h1,h2{{color:#18324b}} .cards{{display:flex;gap:12px;flex-wrap:wrap}} .card{{background:white;border:1px solid #dce4eb;border-radius:9px;padding:14px 18px;min-width:120px}}
.metric{{font-size:25px;font-weight:bold;color:#18324b}} .sub{{font-size:12px;color:#607080}}
.bar{{display:flex;height:26px;border-radius:6px;overflow:hidden;background:#e6ebf0}} .pass{{background:#2b8a63;width:{pass_width:.2f}%}} .fail{{background:#c95050;width:{fail_width:.2f}%}} .blocked{{background:#d39b36;width:{blocked_width:.2f}%}}
table{{border-collapse:collapse;width:100%;background:white;margin:12px 0 24px;font-size:12px}} th,td{{border:1px solid #d5dee6;padding:7px;text-align:left;vertical-align:top;overflow-wrap:anywhere}} th{{background:#18324b;color:white;position:sticky;top:0}} tr:nth-child(even){{background:#f0f4f7}} .PASS{{color:#18794e;font-weight:bold}} .FAIL{{color:#b42318;font-weight:bold}} .BLOCKED{{color:#9a6700;font-weight:bold}} .legend{{font-size:12px;margin-top:6px}}
</style></head><body>
<h1>EduCommerce - Requirement-based Test Execution</h1>
<p>Run time: {escape(datetime.now().astimezone().isoformat(timespec='seconds'))} | Source: <code>test_cases.csv</code></p>
<div class="cards"><div class="card"><div class="sub">Total</div><div class="metric">{total}</div></div>
<div class="card"><div class="sub">PASS</div><div class="metric">{passed}</div></div>
<div class="card"><div class="sub">FAIL</div><div class="metric">{failed}</div></div>
<div class="card"><div class="sub">BLOCKED</div><div class="metric">{blocked}</div></div>
<div class="card"><div class="sub">Pass rate</div><div class="metric">{pass_rate:.1f}%</div></div></div>
<h2>Status distribution</h2><div class="bar"><div class="pass"></div><div class="fail"></div><div class="blocked"></div></div>
<div class="legend">PASS {passed} ({pass_width:.1f}%) &nbsp;|&nbsp; FAIL {failed} ({fail_width:.1f}%) &nbsp;|&nbsp; BLOCKED {blocked} ({blocked_width:.1f}%)</div>
<h2>Summary by requirement</h2><table><tr><th>Requirement</th><th>PASS</th><th>FAIL</th><th>BLOCKED</th><th>Total</th></tr>{req_rows}</table>
<h2>Execution details</h2><table><tr><th>Test case</th><th>REQ</th><th>Scenario</th><th>Expected</th><th>Actual (JSON)</th><th>Status</th><th>ms</th></tr>{table_rows}</table>
<p class="sub">Expected data is read-only. Actual results and execution times are exported separately to reports/test_execution.csv.</p>
</body></html>"""
    html_path = output / "test_dashboard.html"
    html_path.write_text(html_page, encoding="utf-8")

    summary_path = output / "summary_by_requirement.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["requirement_id", "pass", "fail", "blocked", "total"])
        writer.writerows(summary_rows)

    metadata_path = output / "run_summary.json"
    metadata_path.write_text(json.dumps({
        "total": total, "passed": passed, "failed": failed, "blocked": blocked,
        "pass_rate_percent": round(pass_rate, 1),
        "selected_requirements": sorted(by_requirement),
        "generated_at": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"execution_csv": csv_path, "dashboard_html": html_path,
            "summary_csv": summary_path, "summary_json": metadata_path}


def run_suite(csv_path: str | Path | None = None, out_dir: str | Path | None = None):
    source = Path(csv_path) if csv_path else ROOT / "test_cases.csv"
    rows = load_cases(source)
    results = [execute_case(row) for row in rows]
    files = write_reports(results, out_dir or ROOT / "reports")
    counts = Counter(row["status"] for row in results)
    total = len(results)
    print(f"Executed {total} | PASS {counts['PASS']} | FAIL {counts['FAIL']} | BLOCKED {counts['BLOCKED']}")
    print(f"Pass rate: {counts['PASS'] / total * 100:.1f}%")
    print(f"Execution CSV: {files['execution_csv']}")
    print(f"Dashboard: {files['dashboard_html']}")
    for row in results:
        print(f"{row['test_case_id']} | {row['requirement_id']} | {row['status']} | {row['execution_time_ms']} ms | {row['error_message']}")
    return results, files


if __name__ == "__main__":
    run_suite()
