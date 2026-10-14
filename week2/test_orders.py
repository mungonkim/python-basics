"""2주차 문제 B 테스트. 이 파일은 고치지 않는다 (문제지 역할).

실행: uv run pytest week2 -v -k order
"""

import pytest
from orders import parse_order, parse_orders


# 문제 B-1
def test_parse_order_normal():
    assert parse_order("2026-10-14, 사과 ,3,1200") == {
        "date": "2026-10-14",
        "item": "사과",
        "qty": 3,
        "price": 1200,
        "total": 3600,
    }


@pytest.mark.parametrize(
    "line",
    ["2026-10-14,사과,3", "2026-10-14,사과,3,1200,메모", ""],
)
def test_parse_order_wrong_field_count(line):
    with pytest.raises(ValueError, match="칸"):
        parse_order(line)


def test_parse_order_empty_item():
    with pytest.raises(ValueError, match="상품"):
        parse_order("2026-10-14,  ,3,1200")


@pytest.mark.parametrize("qty", ["세개", "2.5", "0", "-1"])
def test_parse_order_bad_qty(qty):
    with pytest.raises(ValueError, match="수량"):
        parse_order(f"2026-10-14,사과,{qty},1200")


@pytest.mark.parametrize("price", ["천원", "-100"])
def test_parse_order_bad_price(price):
    with pytest.raises(ValueError, match="단가"):
        parse_order(f"2026-10-14,사과,3,{price}")


def test_parse_order_free_item_is_ok():
    assert parse_order("2026-10-14,사은품,1,0")["total"] == 0


# 문제 B-2
LINES = [
    "2026-10-14,사과,3,1200",
    "2026-10-14,우유,두개,2500",
    "",
    "2026-10-14,배",
    "2026-10-15,배,2,2000",
    "   ",
]


def test_parse_orders_keeps_good_lines():
    result = parse_orders(LINES)
    assert [o["item"] for o in result["orders"]] == ["사과", "배"]


def test_parse_orders_records_errors():
    errors = parse_orders(LINES)["errors"]
    assert [e["line"] for e in errors] == [2, 4]
    assert "수량" in errors[0]["reason"]
    assert "칸" in errors[1]["reason"]


def test_parse_orders_empty_input():
    assert parse_orders([]) == {"orders": [], "errors": []}
