"""2주차 3일차 테스트. 이 파일은 고치지 않는다 (문제지 역할).

실행: uv run pytest week2 -v -k models
"""

import pytest
from models import Order, OrderBook


def apple():
    return Order("2026-10-14", "사과", 3, 1200)


# 문제 D-1
def test_order_attributes_and_total():
    order = Order("2026-10-14", " 사과 ", 3, 1200)
    assert order.date == "2026-10-14"
    assert order.item == "사과"
    assert order.qty == 3
    assert order.price == 1200
    assert order.total == 3600


@pytest.mark.parametrize(
    ("item", "qty", "price", "word"),
    [("  ", 3, 1200, "상품"), ("사과", 0, 1200, "수량"), ("사과", 3, -1, "단가")],
)
def test_order_validation(item, qty, price, word):
    with pytest.raises(ValueError, match=word):
        Order("2026-10-14", item, qty, price)


def test_order_equality():
    assert apple() == apple()
    assert apple() != Order("2026-10-14", "사과", 4, 1200)


def test_order_to_dict():
    assert apple().to_dict() == {
        "date": "2026-10-14",
        "item": "사과",
        "qty": 3,
        "price": 1200,
        "total": 3600,
    }


def test_order_from_line():
    assert Order.from_line("2026-10-14, 사과 ,3,1200") == apple()
    assert Order.from_line("2026-10-14|사과|3|1200", sep="|") == apple()


@pytest.mark.parametrize(
    ("line", "word"),
    [
        ("2026-10-14,사과,3", "칸"),
        ("2026-10-14,사과,세개,1200", "수량"),
        ("2026-10-14,사과,3,천원", "단가"),
        ("2026-10-14,사과,0,1200", "수량"),
        ("2026-10-14, ,3,1200", "상품"),
    ],
)
def test_order_from_line_errors(line, word):
    with pytest.raises(ValueError, match=word):
        Order.from_line(line)


# 문제 D-2
def make_book():
    return OrderBook(
        [
            apple(),
            Order("2026-10-14", "배", 2, 2000),
            Order("2026-10-15", "사과", 1, 1200),
        ]
    )


def test_book_empty():
    book = OrderBook()
    assert len(book) == 0
    assert book.total_sales() == 0
    assert book.sales_by_item() == {}


def test_book_add_and_len():
    book = OrderBook()
    book.add(apple())
    assert len(book) == 1


def test_empty_books_are_independent():
    first = OrderBook()
    second = OrderBook()
    first.add(apple())
    assert len(second) == 0


def test_book_add_rejects_non_order():
    with pytest.raises(TypeError, match="Order"):
        OrderBook().add({"item": "사과"})


def test_book_sales():
    book = make_book()
    assert book.total_sales() == 8800
    assert book.sales_by_item() == {"사과": 4800, "배": 4000}


def test_book_filter_by_date_returns_new_book():
    book = make_book()
    day = book.filter_by_date("2026-10-14")
    assert isinstance(day, OrderBook)
    assert len(day) == 2
    assert day.total_sales() == 7600
    assert len(book) == 3
