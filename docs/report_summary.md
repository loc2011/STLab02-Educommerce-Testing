# Execution Report Snapshot

- Test suite: `test_cases.csv`
- Selected requirements: REQ-01, REQ-02, REQ-03, REQ-04, REQ-09, REQ-10, REQ-14, REQ-16
- Test cases: 24
- PASS: 24
- FAIL: 0
- BLOCKED: 0
- Pass rate: 100.0%

This run is from the supplied in-memory Python application, executed locally using `python test_runner.py`. It is not a production website test and does not exercise real network, database concurrency, or a real payment gateway.

Important state observation: `TC-PAY-003` matches REQ-10 because it receives `PAYMENT_DECLINED` and creates no order/charge. However, stock for SKU A changes from 20 to 18 because checkout reserves before payment and does not release the reservation when `Payments.collect()` raises. It is not counted as a FAIL against the selected REQ-10 oracle; it is a cross-module inventory risk to confirm and test separately.
