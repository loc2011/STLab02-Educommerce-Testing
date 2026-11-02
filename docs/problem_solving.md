# Part 3 - Problem Solving (summary)

## 3.1 Two SKU, one SKU is out of stock

**Expected:** With A=2 and B=100 while A has enough but B does not, `Inventory.reserve()` must raise `OUT_OF_STOCK` before decrementing any stock. A and B stock before/after remain identical. The supplied `Inventory.reserve()` already performs a complete availability pass followed by a decrement pass, so its current structure supports atomicity for the modeled single-threaded lab.

**Impacted code:** `ecommerce_app.py → Inventory.reserve(lines)`; `Checkout.place()` calls reserve during checkout.

**Test ideas:** (1) A=2/B=100 with B stock insufficient: expected `OUT_OF_STOCK`, both stocks unchanged. (2) A and B both sufficient: reserve succeeds and each stock is decremented by requested quantity. Capture stock snapshot before/after and exception.

## 3.2 Voucher is marked used only after success

**Expected:** On ONLINE declined, no order is created and `customer.used_codes` must not contain SAVE10. On successful order creation, SAVE10 is added to `used_codes`. In the supplied `Checkout.place()`, `used_codes.add(voucher)` occurs only after an order is stored; therefore a declined payment does not mark the voucher used. A separate stock rollback issue is visible after declined payment and is noted in the report.

**Impacted code:** `ecommerce_app.py → Checkout.place()` after `orders` and `by_key` updates.

**Test ideas:** (1) SAVE10 + online approved=False: expected PAYMENT_DECLINED, zero orders, SAVE10 not used. (2) SAVE10 + COD success: expected one order and SAVE10 in used_codes. Evidence: before/after used_codes, order count, payment state.

## 3.3 Unknown payment method WALLET

**Expected:** Method outside COD/ONLINE must raise `INVALID_PAYMENT_METHOD` and no order should be created. The supplied code validates the method inside `Payments.collect()`, which is called after `Inventory.reserve()`. There is no exception handler in `Checkout.place()` that releases reserved stock; observed stock therefore decreases even though the payment method is rejected.

**Impacted code:** `ecommerce_app.py → Checkout.place()` ordering around `inventory.reserve()` and `payments.collect()`; `Payments.collect()` raises the error.

**Suggested improvement:** Validate the payment method before reserving stock, or wrap the transaction and release stock on every failed payment/unsupported method. Keep a state rollback assertion.

**Test ideas:** (1) WALLET: INVALID_PAYMENT_METHOD, zero order, zero charges, stock unchanged. (2) COD or approved ONLINE: successful order state and expected stock effect. The first case's no-stock-change expectation is a transactional safety assumption beyond the literal REQ-16 criterion and should be confirmed with BA/PO or linked to the inventory rollback rule.

## 3.4 Product price changes between add-to-cart and checkout

**Ambiguity:** Requirements state that subtotal uses current product price but do not state whether price is locked when item is added, when checkout begins, or at order creation. The sample `Cart.subtotal()` reads price from Catalog when called, so a price change before checkout is reflected in the later subtotal.

**BA/PO questions:** Is price locked at add-to-cart? If not, should user be notified when it changes? Does checkout re-confirm the final amount before payment? What happens if price changes during payment redirect?

**Test ideas:** (1) Add A at 200,000, change Catalog to 220,000 before checkout; compare expected according to confirmed price-lock rule. (2) Change price after checkout summary but before Place Order; verify amount confirmation/consistency. Keep expected marked pending until rule confirmation.

## 3.5 Same SKU added twice

**Expected:** Adding A×2 then A×3 results in one CartLine A quantity 5 and subtotal 1,000,000 VND. The supplied `Cart.add()` searches an existing SKU and increments quantity.

**Impacted code:** `ecommerce_app.py → Cart.add()` and `Cart.subtotal()`.

**Test ideas:** (1) Add A×2 then A×3; verify one line and quantity 5. (2) Add A×2, B×1, A×3; verify two lines, A quantity 5, subtotal 1,300,000. (3) Add quantity 0 or negative; expect INVALID_QUANTITY and unchanged cart.

## 3.6 Data-driven tests share state

**Risk:** Reusing one Checkout/Catalog across rows means one case's stock decrement, price change, `used_codes`, orders or payment charges can contaminate the next test. Result may depend on execution order.

**Impacted code:** `fixture()` and `test_runner.py → execute_case()`.

**Change:** Create service/customer/cart inside `execute_case()` for each row. Do not reuse mutable fixture objects globally. Capture initial and final state.

**Test ideas:** (1) Two fixture() calls return independent object identities and default stock/price. (2) Mutate stock/price/customer state in fixture A; verify fixture B retains defaults. Run test list in reversed order and compare result vector.

## 3.7 Dashboard shows PASS despite skipped malformed rows

**Expected:** If CSV has 20 rows and 3 malformed rows, dashboard cannot report 17/17 PASS as 100% of the supplied suite. All 20 input rows must be accounted for; malformed cases should be BLOCKED or rejected before execution with a clear count and error. Denominator for pass rate must be total supplied cases, not successfully parsed cases only.

**Impacted code:** `test_runner.py → load_cases()`, `execute_case()`, `write_reports()`.

**Change:** Validate schema, duplicate IDs, row count and JSON input. Do not drop rows. Invalid row data becomes BLOCKED and remains in total; duplicate IDs/missing header aborts suite with a clear error.

**Test ideas:** (1) Add a row with malformed input_json; expected one BLOCKED row, total unchanged. (2) Add duplicate test_case_id; expected runner raises DUPLICATE_TEST_IDS instead of producing a partial report. Evidence: source row count vs execution count.

## 3.8 Shipping threshold changes from 500k to 700k

**Impact:** Update acceptance rule REQ-09; conditions for inner-zone threshold; scenarios at 699,999 / 700,000 / 700,001; CSV data and expected values; `Shipping.calculate()` threshold constant; summary/coverage and regression cases that calculate order total. Outer-zone 50,000 rule remains unchanged.

**Test ideas:** (1) Inner subtotal 699,999 -> 30,000. (2) Inner subtotal 700,000 -> 0. (3) Outer subtotal 700,000 -> 50,000. Run regression for checkout total and any flow where voucher/discount is present; confirm whether shipping threshold uses pre-voucher subtotal (Instruction says pre-discount subtotal).
