"""1주차 점검 문제 테스트. 이 파일은 고치지 않는다 (문제지 역할).

실행: uv run pytest week1 -v
"""

from problems import (
    chunk,
    count_words,
    even_squares,
    group_by_category,
    parse_order,
    summarize_prices,
    top_n,
    unique_in_order,
)

PRODUCTS = [
    {"name": "사과", "category": "과일", "price": 1000},
    {"name": "우유", "category": "유제품", "price": 2500},
    {"name": "배", "category": "과일", "price": 2000},
]


# 문제 1
def test_count_words_basic():
    assert count_words("Hi, hi! Bye.") == {"hi": 2, "bye": 1}


def test_count_words_question_and_spaces():
    assert count_words("  Is it  AI?  it is ") == {"is": 2, "it": 2, "ai": 1}


def test_count_words_empty():
    assert count_words("") == {}


# 문제 2
def test_top_n_ties_sorted_by_word():
    assert top_n({"b": 2, "a": 2, "c": 5}, 2) == [("c", 5), ("a", 2)]


def test_top_n_default_three():
    counts = {"x": 1, "y": 4, "z": 3, "w": 2}
    assert top_n(counts) == [("y", 4), ("z", 3), ("w", 2)]


def test_top_n_fewer_than_n():
    assert top_n({"only": 1}, 5) == [("only", 1)]


# 문제 3
def test_unique_in_order():
    assert unique_in_order([3, 1, 3, 2, 1]) == [3, 1, 2]


def test_unique_in_order_strings_and_empty():
    assert unique_in_order(["a", "b", "a"]) == ["a", "b"]
    assert unique_in_order([]) == []


# 문제 4
def test_even_squares():
    assert even_squares([1, 2, 3, 4]) == [4, 16]


def test_even_squares_negative_and_zero():
    assert even_squares([-2, 0, 5]) == [4, 0]


# 문제 5
def test_group_by_category():
    assert group_by_category(PRODUCTS) == {"과일": ["사과", "배"], "유제품": ["우유"]}


def test_group_by_category_empty():
    assert group_by_category([]) == {}


# 문제 6
def test_summarize_prices():
    assert summarize_prices(PRODUCTS) == {
        "count": 3,
        "min": 1000,
        "max": 2500,
        "avg": 1833.3,
    }


def test_summarize_prices_empty():
    assert summarize_prices([]) == {"count": 0, "min": None, "max": None, "avg": None}


# 문제 7
def test_parse_order_strips_spaces():
    assert parse_order("2026-10-14, 사과 ,3,1200") == {
        "date": "2026-10-14",
        "item": "사과",
        "qty": 3,
        "price": 1200,
        "total": 3600,
    }


def test_parse_order_custom_sep():
    result = parse_order("2026-10-14|우유|1|2500", sep="|")
    assert result["item"] == "우유"
    assert result["total"] == 2500


# 문제 8
def test_chunk_default_size():
    assert chunk([1, 2, 3, 4, 5]) == [[1, 2], [3, 4], [5]]


def test_chunk_size_three_and_empty():
    assert chunk([1, 2, 3, 4], 3) == [[1, 2, 3], [4]]
    assert chunk([], 3) == []
