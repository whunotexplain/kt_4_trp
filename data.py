"""
Работа с данными заказов: чтение/запись CSV-файла, справочники для выпадающих списков.
"""
import csv
import os
from dataclasses import dataclass, asdict

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.csv")

FIELDNAMES = [
    "order_id", "date_created", "date_due", "service_name", "service_category",
    "description", "executor", "status", "base_cost", "discount_percent",
    "final_cost", "payment_method", "client_comment",
]

CATEGORIES = ["Консультации", "Ремонт", "Доставка", "Обучение", "Другое"]
STATUSES = ["Новый", "В работе", "Выполнен", "Отменён"]
PAYMENT_METHODS = ["Онлайн", "Банковский перевод", "При получении"]
EXECUTORS = [
    "Иванов А.А.", "Петрова М.И.", "Сидоров В.П.", "Кузнецова Е.В.",
    "Смирнов Д.К.", "Волков С.Т.", "Морозова Л.Н.", "Фёдоров И.Р.",
    "Григорьев П.О.", "Лебедева А.С.",
]

# Цвета подсветки строк
COLOR_IN_PROGRESS = "#FFFFE0"   # В работе
COLOR_DONE = "#E0F7FA"          # Выполнен
COLOR_CANCELLED = "#FFCDD2"     # Отменён
COLOR_BIG_DISCOUNT = "#2E8B57"  # скидка > 20%
COLOR_DEFAULT = "#FFFFFF"

PAYMENT_ON_DELIVERY_MARK = "card-> money"


@dataclass
class Order:
    order_id: str
    date_created: str
    date_due: str
    service_name: str
    service_category: str
    description: str
    executor: str
    status: str
    base_cost: float
    discount_percent: float
    final_cost: float
    payment_method: str
    client_comment: str

    @classmethod
    def from_row(cls, row: dict) -> "Order":
        return cls(
            order_id=row["order_id"],
            date_created=row["date_created"],
            date_due=row["date_due"],
            service_name=row["service_name"],
            service_category=row["service_category"],
            description=row["description"],
            executor=row["executor"],
            status=row["status"],
            base_cost=float(row["base_cost"] or 0),
            discount_percent=float(row["discount_percent"] or 0),
            final_cost=float(row["final_cost"] or 0),
            payment_method=row["payment_method"],
            client_comment=row["client_comment"],
        )

    def to_row(self) -> dict:
        d = asdict(self)
        d["base_cost"] = f"{self.base_cost:.2f}"
        d["discount_percent"] = f"{self.discount_percent:.0f}"
        d["final_cost"] = f"{self.final_cost:.2f}"
        return d


def load_orders() -> list:
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [Order.from_row(row) for row in reader]


def save_orders(orders: list) -> None:
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for order in orders:
            writer.writerow(order.to_row())


def generate_order_id(orders: list) -> str:
    max_num = 1000
    for o in orders:
        digits = "".join(ch for ch in o.order_id if ch.isdigit())
        if digits:
            max_num = max(max_num, int(digits))
    return f"O{max_num + 1}"


def row_color(order: "Order") -> str:
    """Цвет фона строки по правилам приоритета: скидка > 20% важнее статуса."""
    if order.discount_percent > 20:
        return COLOR_BIG_DISCOUNT
    return {
        "В работе": COLOR_IN_PROGRESS,
        "Выполнен": COLOR_DONE,
        "Отменён": COLOR_CANCELLED,
    }.get(order.status, COLOR_DEFAULT)
