"""EduCommerce application used by the STLab02 practice instruction.

This is an in-memory teaching application. The business implementation is
intentionally kept aligned with the supplied Instruction; the testing project
must observe implementation behavior rather than silently patch it.
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP


def D(value):
    return Decimal(str(value))


def money(value):
    return D(value).quantize(D("1"), rounding=ROUND_HALF_UP)


@dataclass
class Product:
    sku: str
    title: str
    price: Decimal
    stock: int
    active: bool = True


@dataclass
class Customer:
    customer_id: str
    authenticated: bool = True
    used_codes: set = field(default_factory=set)


@dataclass
class CartLine:
    sku: str
    quantity: int


@dataclass
class Voucher:
    code: str
    percent: int
    min_subtotal: Decimal
    cap: Decimal
    active: bool = True


@dataclass
class Order:
    order_id: str
    customer_id: str
    total: Decimal
    status: str
    lines: list
    discount: Decimal
    shipping: Decimal
    payment_method: str


class Catalog:
    def __init__(self):
        self.products = {
            "A": Product("A", "Wireless Mouse", D(200000), 20),
            "B": Product("B", "Mechanical Keyboard", D(300000), 15),
            "C": Product("C", "USB-C Hub", D(150000), 12),
        }

    def get(self, sku):
        product = self.products.get(sku)
        if not product or not product.active:
            raise ValueError("PRODUCT_UNAVAILABLE")
        return product


class Cart:
    def __init__(self, catalog):
        self.catalog = catalog
        self.lines = []

    def add(self, sku, quantity):
        self.catalog.get(sku)
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("INVALID_QUANTITY")
        existing = next((line for line in self.lines if line.sku == sku), None)
        if existing:
            existing.quantity += quantity
        else:
            self.lines.append(CartLine(sku, quantity))

    def subtotal(self):
        return sum(
            (self.catalog.get(line.sku).price * line.quantity for line in self.lines),
            D(0),
        )


class Inventory:
    def __init__(self, catalog):
        self.catalog = catalog

    def reserve(self, lines):
        # Check all requested quantities first; only then mutate stock.
        for line in lines:
            if self.catalog.get(line.sku).stock < line.quantity:
                raise ValueError("OUT_OF_STOCK")
        for line in lines:
            self.catalog.get(line.sku).stock -= line.quantity

    def release(self, lines):
        for line in lines:
            self.catalog.get(line.sku).stock += line.quantity


class Promotions:
    def __init__(self):
        self.codes = {"SAVE10": Voucher("SAVE10", 10, D(500000), D(100000))}

    def discount(self, code, subtotal, customer):
        if not code:
            return D(0)
        voucher = self.codes.get(code)
        if not voucher or not voucher.active:
            raise ValueError("INVALID_VOUCHER")
        if not customer.authenticated:
            raise ValueError("LOGIN_REQUIRED")
        if code in customer.used_codes:
            raise ValueError("VOUCHER_USED")
        # Kept as shown in the Instruction (REQ-06 is outside selected scope).
        if subtotal <= voucher.min_subtotal:
            raise ValueError("MIN_SUBTOTAL_NOT_MET")
        return min(money(subtotal * voucher.percent / D(100)), voucher.cap)


class Shipping:
    def calculate(self, subtotal, area):
        if area not in ("inner", "outer"):
            raise ValueError("INVALID_AREA")
        if area == "inner" and subtotal >= D(500000):
            return D(0)
        return D(30000) if area == "inner" else D(50000)


class Payments:
    def __init__(self):
        self.charges = []

    def collect(self, amount, method, approved, key):
        if method == "COD":
            return "PENDING_COD"
        if method != "ONLINE":
            raise ValueError("INVALID_PAYMENT_METHOD")
        if not approved:
            raise ValueError("PAYMENT_DECLINED")
        self.charges.append({"key": key, "amount": amount})
        return "PAID"


class Checkout:
    def __init__(self, catalog=None):
        self.catalog = catalog or Catalog()
        self.inventory = Inventory(self.catalog)
        self.promotions = Promotions()
        self.shipping = Shipping()
        self.payments = Payments()
        self.orders = {}
        self.by_key = {}
        self.counter = 0

    def place(
        self,
        customer,
        cart,
        area="inner",
        voucher=None,
        method="COD",
        approved=True,
        key="REQ-001",
    ):
        if not customer.authenticated:
            raise ValueError("LOGIN_REQUIRED")
        if not cart.lines:
            raise ValueError("EMPTY_CART")
        subtotal = cart.subtotal()
        discount = self.promotions.discount(voucher, subtotal, customer)
        shipping = self.shipping.calculate(subtotal, area)
        total = max(D(0), subtotal - discount + shipping)
        self.inventory.reserve(cart.lines)
        # Ordering intentionally mirrors the supplied Instruction.
        if key in self.by_key:
            return self.orders[self.by_key[key]]
        payment_state = self.payments.collect(total, method, approved, key)
        self.counter += 1
        order = Order(
            f"ORD-{self.counter:04d}",
            customer.customer_id,
            total,
            payment_state,
            [(line.sku, line.quantity) for line in cart.lines],
            discount,
            shipping,
            method,
        )
        self.orders[order.order_id] = order
        self.by_key[key] = order.order_id
        if voucher:
            customer.used_codes.add(voucher)
        return order


# Every call creates a clean application/customer/cart; no global state is shared.
_FIXTURE_LINES = {
    "catalog_default": [],
    "empty_cart": [],
    "a1": [("A", 1)],
    "a2": [("A", 2)],
    "a2_b1": [("A", 2), ("B", 1)],
    "a1_b1": [("A", 1), ("B", 1)],
    "b1": [("B", 1)],
    "a1_b2_c1": [("A", 1), ("B", 2), ("C", 1)],
}


def fixture(fixture_key="a1", config=None):
    """Create an isolated (Checkout, Customer, Cart) test environment."""
    if fixture_key not in _FIXTURE_LINES:
        raise ValueError("UNKNOWN_FIXTURE")
    config = config or {}
    service = Checkout()
    customer = Customer(
        config.get("customer_id", "U_TEST"),
        authenticated=config.get("authenticated", True),
        used_codes=set(config.get("used_codes", [])),
    )
    cart = Cart(service.catalog)

    for sku, updates in config.get("product_updates", {}).items():
        if sku not in service.catalog.products:
            raise ValueError("UNKNOWN_PRODUCT_IN_FIXTURE")
        product = service.catalog.products[sku]
        if "active" in updates:
            product.active = bool(updates["active"])
        if "price" in updates:
            product.price = D(updates["price"])
        if "stock" in updates:
            product.stock = int(updates["stock"])

    for sku, quantity in _FIXTURE_LINES[fixture_key]:
        cart.add(sku, quantity)
    for sku, quantity in config.get("extra_lines", []):
        cart.add(sku, quantity)
    return service, customer, cart
