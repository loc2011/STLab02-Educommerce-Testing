# Test Conditions, Scenarios & Traceability Summary

| REQ | Conditions | Scenarios | Test cases |
|---|---|---|---|
| REQ-01 | COND-CAT-01: active; COND-CAT-02: inactive/missing | TS-CAT-01 active lookup; TS-CAT-02 inactive reject; TS-CAT-03 unknown SKU reject | TC-CAT-001..003 |
| REQ-02 | COND-CART-01: positive integer; COND-CART-02: merge/invalid | TS-CART-01 add positive; TS-CART-02 merge same SKU; TS-CART-03 quantity zero reject | TC-CART-001..003 |
| REQ-03 | COND-PRICE-01: Decimal arithmetic; COND-PRICE-02: updated price | TS-PRICE-01 multi-SKU sum; TS-PRICE-02 decimal scale; TS-PRICE-03 price update reflected | TC-PRICE-001..003 |
| REQ-04 | COND-AUTH-01: guest; COND-AUTH-02: authenticated | TS-AUTH-01 guest COD reject; TS-AUTH-02 guest ONLINE reject; TS-AUTH-03 authenticated checkout | TC-AUTH-001..003 |
| REQ-09 | COND-SHP-01: inner threshold; COND-SHP-02: outer zone | TS-SHP-01 inner below threshold; TS-SHP-02 exact threshold; TS-SHP-03 outer fixed fee | TC-SHP-001..003 |
| REQ-10 | COND-PAY-01: COD; COND-PAY-02: ONLINE outcome | TS-PAY-01 COD pending; TS-PAY-02 approved paid; TS-PAY-03 declined no order | TC-PAY-001..003 |
| REQ-14 | COND-EMPTY-01: empty cart; COND-EMPTY-02: non-empty | TS-EMPTY-01 empty COD reject; TS-EMPTY-02 empty ONLINE reject; TS-EMPTY-03 non-empty checkout | TC-EMPTY-001..003 |
| REQ-16 | COND-METHOD-01: unsupported; COND-METHOD-02: allowed | TS-METHOD-01 WALLET reject; TS-METHOD-02 BANK reject; TS-METHOD-03 COD accepted | TC-METHOD-001..003 |

Total: 16 test conditions, 24 scenarios/cases traced across 8 REQs; 10 negative/rejection scenarios plus 2 boundary scenarios for shipping threshold. Every CSV row contains requirement_id, condition_id, scenario_id and unique test_case_id.

## Test data / fixture map

| fixture_key | Initial cart | Purpose |
|---|---|---|
| `catalog_default` | Empty | Isolated Catalog lookups |
| `empty_cart` | Empty | REQ-14 and Cart.add positive case |
| `a1` | A × 1 | Checkout authentication/payment/method |
| `a2` | A × 2 | Checkout/payment outcome |
| `a2_b1` | A × 2, B × 1 | Multi-SKU subtotal |
| `a1_b1` | A × 1, B × 1 | Decimal precision and shipping test input |

The runner calls `fixture()` for every case, then applies per-row `fixture_config` (such as active state or decimal prices). Each test receives a new Checkout, Catalog, Customer, and Cart.
