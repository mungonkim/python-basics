"""2주차 2일차. 파일 입출력과 JSON.

1일차의 parse_orders로 CSV 파일을 읽어 정리하고, 결과를 JSON 파일로 저장한다.
함수 설명(docstring)을 읽고 `raise NotImplementedError` 줄을 지운 뒤 직접 구현한다.
확인: uv run pytest week2 -v -k report
직접 실행: uv run python week2/report.py week2/sample_orders.csv out/report.json
"""

import json
import sys
from pathlib import Path

from orders import parse_orders

HEADER = "날짜,상품,수량,단가"


# 문제 C-1. 파일 읽기
def load_orders(path):
    """CSV 파일을 읽어 parse_orders 결과를 돌려준다.

    - 파일은 UTF-8이다. 엑셀에서 저장한 CSV는 맨 앞에 BOM이 붙어 있을 수 있는데, 그래도 읽혀야 한다.
    - 첫 줄은 헤더(HEADER)다. 헤더는 주문으로 처리하지 않는다.
    - 첫 줄이 헤더와 다르거나 파일이 비어 있으면 ValueError (메시지에 "헤더").
    - 파일이 없으면 FileNotFoundError가 그대로 나가게 둔다 (여기서 잡지 않는다).
    - errors의 "line"은 **파일의 실제 줄 번호**다. 헤더가 1번 줄이므로 첫 주문은 2번 줄.
    돌려주는 값: {"orders": [...], "errors": [{"line": 줄 번호, "reason": 이유}, ...]}
    """

    with open(path, "r", encoding="utf-8-sig") as f:
        first_line = f.readline()

        if not first_line:
            raise ValueError("헤더가 올바르지 않거나 파일이 비어있습니다.")

        if first_line.strip() != HEADER:
            raise ValueError("헤더 형식이 일치하지 않습니다.")

        data_lines = f.readlines()

    result = parse_orders(data_lines, sep=",")

    for error in result["errors"]:
        error["line"] += 1

    return result


# 문제 C-2. 요약
def summarize(orders):
    """정상 주문 목록을 요약한다.

    돌려주는 값:
    {"count": 주문 수, "total_qty": 수량 합계, "total_sales": 매출 합계(total의 합),
     "sales_by_item": {상품: 매출 합계, ...}}
    - sales_by_item은 상품이 처음 나온 순서대로.
    - 주문이 없으면 count, total_qty, total_sales는 0, sales_by_item은 {}.
    """
    if not orders:
        return {"count": 0, "total_qty": 0, "total_sales": 0, "sales_by_item": {}}

    count = len(orders)
    total_qty = 0
    total_sales = 0
    sales_by_item = {}

    for order in orders:
        item = order["item"]
        qty = order["qty"]
        total = order["total"]

        total_qty += qty
        total_sales += total

        if item in sales_by_item:
            sales_by_item[item] += total
        else:
            sales_by_item[item] = total

    return {
        "count": count,
        "total_qty": total_qty,
        "total_sales": total_sales,
        "sales_by_item": sales_by_item,
    }


# 문제 C-3. JSON 저장과 불러오기
def save_report(report, path):
    """딕셔너리를 JSON 파일로 저장한다.

    - UTF-8로 저장하고, 한글이 "\uc0ac" 같은 코드가 아니라 글자 그대로 보이게 한다.
    - 들여쓰기 2칸으로 사람이 읽기 좋게 저장한다.
    - 저장할 폴더가 없으면 만든다.
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(path_obj, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def load_report(path):
    """save_report로 저장한 JSON 파일을 다시 딕셔너리로 읽는다."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# 문제 C-4. 전체 흐름
def run(input_path, output_path):
    """CSV를 읽고 → 요약하고 → JSON으로 저장한 뒤, 저장한 딕셔너리를 돌려준다.

    저장 형식: {"source": 입력 파일 이름(폴더 빼고), "summary": summarize 결과, "errors": 오류 목록}
    """
    parsed = load_orders(input_path)

    summary = summarize(parsed["orders"])

    report = {
        "source": Path(input_path).name,
        "summary": summary,
        "errors": parsed["errors"],
    }

    save_report(report, output_path)

    return report


def main(argv):
    """명령줄 실행용. 테스트는 없다. 직접 실행해서 확인한다.

    - 인자가 2개(입력 CSV, 출력 JSON)가 아니면 사용법을 출력하고 2를 돌려준다.
    - 입력 파일이 없거나 헤더가 틀리면 트레이스백 대신 알아보기 쉬운 한 줄 안내를 출력하고 1을 돌려준다.
    - 성공하면 "주문 N건, 오류 M건, 저장: 경로"를 출력하고 0을 돌려준다.
    """

    # 2단계: 인자가 2개가 아니면 사용법 출력 후 return 2
    if len(argv) != 2:
        print("사용법: report.py <입력_CSV_경로> <출력_JSON_경로>")
        return 2

    input_path = argv[0]
    output_path = argv[1]

    # 3단계 & 4단계: try/except로 run 실행 및 예외 한 줄 처리
    try:
        report = run(input_path, output_path)
    except FileNotFoundError:
        print(f"오류: 파일 '{input_path}'을(를) 찾을 수 없습니다.")
        return 1
    except ValueError as e:
        # 헤더 오류 등 데이터 이상 발생 시 트레이스백 대신 한 줄 메시지 출력
        print(f"오류: 입력 파일을 처리할 수 없습니다 ({e})")
        return 1

    # 5단계: 성공 시 결과 출력 후 return 0
    count = report["summary"]["count"]
    errors_count = len(report["errors"])
    print(f"주문 {count}건, 오류 {errors_count}건, 저장: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
