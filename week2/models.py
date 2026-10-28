"""2주차 3일차. 타입 힌트와 클래스.

지금까지 주문은 딕셔너리({"date": ..., "item": ...})였다. 오늘은 주문을 클래스로 만든다.
- 함수와 메서드에 타입 힌트를 직접 붙인다. 아래 뼈대에는 일부러 힌트가 없다.
- 확인 1: uv run pytest week2 -v -k models
- 확인 2: uv run mypy --strict week2/models.py  (타입 힌트 검사, mypy는 직접 설치)
"""


# 문제 D-1. 주문 클래스
class Order:
    """주문 한 건.

    만들기: Order("2026-10-14", "사과", 3, 1200)  (date: str, item: str, qty: int, price: int)
    - 만들 때 검사한다. 잘못되면 ValueError (메시지 단어는 1일차와 같다)
      - item이 비었거나 공백뿐이면 "상품" / qty가 1보다 작으면 "수량" / price가 0보다 작으면 "단가"
    - item은 앞뒤 공백을 지워서 저장한다.
    - 내용이 같은 두 Order는 == 로 비교하면 True다.
    """

    date: str
    item: str
    qty: int
    price: int

    def __init__(self, date: str, item: str, qty: int, price: int):
        item = item.strip()

        if not item:
            raise ValueError("상품 이름이 비어 있거나 공백입니다.")

        if qty < 1:
            raise ValueError("수량이 1개 이상이어야 합니다.")

        if price < 0:
            raise ValueError("단가는 0원 이상이어야 한다")

        self.date = date
        self.item = item
        self.qty = qty
        self.price = price

    @property
    def total(self) -> int:
        """qty x price. 괄호 없이 order.total 로 읽혀야 한다 (메서드가 아니라 속성처럼)."""
        return self.qty * self.price

    def to_dict(self) -> dict[str | int, str | int]:
        """1일차 parse_order와 같은 모양의 딕셔너리로 바꾼다 (total 포함)."""
        return {
            "date": self.date,
            "item": self.item,
            "qty": self.qty,
            "price": self.price,
            "total": self.total,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return (
            self.date == other.date
            and self.item == other.item
            and self.qty == other.qty
            and self.price == other.price
            and self.total == other.total
        )

    @classmethod
    def from_line(cls, line: str, sep: str = ",") -> Order:
        """주문 한 줄("날짜,상품,수량,단가")로 Order를 만든다.

        - 칸이 4개가 아니면 ValueError ("칸"), 수량 · 단가가 정수가 아니면 ValueError ("수량" / "단가")
        - 그 밖의 검사는 __init__에 맡긴다 (같은 검사를 두 번 쓰지 않는다).
        """
        parts = line.split(sep)

        if len(parts) != 4:
            raise ValueError("입력된 칸의 개수가 올바르지 않습니다.")

        qty_str = parts[2].strip()
        price_str = parts[3].strip()

        try:
            qty = int(qty_str)
        except ValueError as e:
            raise ValueError("수량이 정수가 아닙니다.") from e

        try:
            price = int(price_str)
        except ValueError as e:
            raise ValueError("단가가 정수가 아닙니다.") from e

        return cls(parts[0].strip(), parts[1].strip(), qty, price)


# 문제 D-2. 주문 장부 클래스
class OrderBook:
    """Order 여러 개를 담는 장부.

    만들기: OrderBook() 또는 OrderBook([order1, order2])
    - 주문 없이 만든 장부 두 개는 서로 독립이어야 한다 (한쪽에 add해도 다른 쪽은 그대로).
    """

    def __init__(self, orders: list[Order] | None = None) -> None:
        self.orders = [] if orders is None else list(orders)

    def add(self, order: Order) -> None:
        """주문을 하나 추가한다. Order가 아니면 TypeError (메시지에 "Order")."""
        if not isinstance(order, Order):
            raise TypeError("Order must be an Order")
        self.orders.append(order)

    def __len__(self) -> int:
        return len(self.orders)

    def total_sales(self) -> int:
        """모든 주문의 total 합계. 주문이 없으면 0."""
        return sum(order.total for order in self.orders)

    def sales_by_item(self) -> dict[str, int]:
        """{상품: 매출 합계}. 상품이 처음 나온 순서대로."""
        result: dict[str, int] = {}

        for order in self.orders:
            if order.item not in result:
                result[order.item] = 0
            result[order.item] += order.total

        return result

    def filter_by_date(self, date: str) -> OrderBook:
        """그 날짜의 주문만 담은 **새** OrderBook을 돌려준다. 원래 장부는 바뀌지 않는다."""
        filtered = [order for order in self.orders if order.date == date]

        return OrderBook(filtered)
