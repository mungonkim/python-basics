"""2주차 2일차 테스트. 이 파일은 고치지 않는다 (문제지 역할).

tmp_path: pytest가 테스트마다 만들어 주는 빈 임시 폴더(Path). 테스트가 끝나면 신경 쓰지 않아도 된다.
실행: uv run pytest week2 -v -k report
"""

import pytest
from report import HEADER, load_orders, load_report, run, save_report, summarize

CSV_TEXT = (
    f"{HEADER}\n"
    "2026-10-14,사과,3,1200\n"
    "2026-10-14,우유,두개,2500\n"
    "\n"
    "2026-10-15,배,2,2000\n"
    "2026-10-15,사과,1,1200\n"
)


def write_csv(folder, text, encoding="utf-8"):
    path = folder / "orders.csv"
    path.write_text(text, encoding=encoding)
    return path


# 문제 C-1
def test_load_orders_reads_korean(tmp_path):
    result = load_orders(write_csv(tmp_path, CSV_TEXT))
    assert [o["item"] for o in result["orders"]] == ["사과", "배", "사과"]


def test_load_orders_error_line_is_file_line(tmp_path):
    errors = load_orders(write_csv(tmp_path, CSV_TEXT))["errors"]
    assert [e["line"] for e in errors] == [3]
    assert "수량" in errors[0]["reason"]


def test_load_orders_with_bom(tmp_path):
    result = load_orders(write_csv(tmp_path, CSV_TEXT, encoding="utf-8-sig"))
    assert len(result["orders"]) == 3


def test_load_orders_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_orders(tmp_path / "없는파일.csv")


@pytest.mark.parametrize("text", ["", "date,item,qty,price\n2026-10-14,사과,3,1200\n"])
def test_load_orders_bad_header(tmp_path, text):
    with pytest.raises(ValueError, match="헤더"):
        load_orders(write_csv(tmp_path, text))


# 문제 C-2
def test_summarize():
    orders = load_orders_from_text(CSV_TEXT)
    assert summarize(orders) == {
        "count": 3,
        "total_qty": 6,
        "total_sales": 8800,
        "sales_by_item": {"사과": 4800, "배": 4000},
    }


def test_summarize_empty():
    assert summarize([]) == {
        "count": 0,
        "total_qty": 0,
        "total_sales": 0,
        "sales_by_item": {},
    }


def load_orders_from_text(text):
    from orders import parse_orders

    return parse_orders(text.splitlines()[1:])["orders"]


# 문제 C-3
def test_save_and_load_report_roundtrip(tmp_path):
    report = {"이름": "사과", "값": [1, 2]}
    path = tmp_path / "out" / "report.json"
    save_report(report, path)
    assert load_report(path) == report


def test_save_report_keeps_korean_and_indent(tmp_path):
    path = tmp_path / "report.json"
    save_report({"상품": "사과"}, path)
    text = path.read_text(encoding="utf-8")
    assert "사과" in text
    assert '\n  "상품"' in text


# 문제 C-4
def test_run(tmp_path):
    out = tmp_path / "result" / "report.json"
    report = run(write_csv(tmp_path, CSV_TEXT), out)
    assert report["source"] == "orders.csv"
    assert report["summary"]["total_sales"] == 8800
    assert report["errors"][0]["line"] == 3
    assert load_report(out) == report
