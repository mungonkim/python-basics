"""2주차 1일차 문제 B. 잘못된 주문 줄을 예외로 다루기.

1주차 parse_order는 칸이 모자라면 IndexError, 수량이 숫자가 아니면 ValueError가
제각각 났다. 이번에는 무엇이 잘못됐는지 알려 주는 ValueError 하나로 통일하고,
여러 줄을 처리할 때는 잘못된 줄만 건너뛰고 기록을 남긴다.
확인: uv run pytest week2 -v -k order
"""


# 문제 B-1. 검사하고 예외 내기
def parse_order(line, sep=","):
    """주문 한 줄을 딕셔너리로 바꾼다. 형식은 1주차와 같다: "날짜{sep}상품{sep}수량{sep}단가"

    정상: parse_order("2026-10-14, 사과 ,3,1200")
        -> {"date": "2026-10-14", "item": "사과", "qty": 3, "price": 1200, "total": 3600}
    잘못된 줄은 모두 ValueError를 내고, 메시지에 아래 단어가 들어가게 한다.
    - 칸이 4개가 아니면 (모자라거나 많으면): "칸"
    - 상품이 비어 있으면: "상품"
    - 수량이 정수가 아니거나 1보다 작으면: "수량"
    - 단가가 정수가 아니거나 0보다 작으면: "단가"
    """

    parts = line.split(sep)

    if len(parts) != 4:
        raise ValueError("입력된 칸의 개수가 올바르지 않습니다.")

    date = parts[0].strip()
    item = parts[1].strip()
    qty = parts[2].strip()
    price = parts[3].strip()

    if not item:
        raise ValueError("상품이 비어있습니다.")

    try:
        qty = int(qty)
    except ValueError as e:
        raise ValueError("수량 형식이 올바르지 않습니다.") from e

    if qty < 1:
        raise ValueError("수량은 1개 이상이어야 합니다.")

    try:
        price = int(price)
    except ValueError as e:
        raise ValueError("단가 형식이 올바르지 않습니다.") from e

    if price < 0:
        raise ValueError("단가는 0 이상이어야 합니다.")

    return {
        "date": date,
        "item": item,
        "qty": qty,
        "price": price,
        "total": qty * price,
    }


# 문제 B-2. 잡아서 기록하고 계속 가기
def parse_orders(lines, sep=","):
    """여러 줄을 처리한다. 잘못된 줄이 있어도 멈추지 않는다.

    돌려주는 값: {"orders": [정상 주문 딕셔너리...], "errors": [{"line": 줄 번호, "reason": 이유}...]}
    - 줄 번호는 1부터 센다.
    - reason은 parse_order가 낸 ValueError의 메시지 문자열이다.
    - 빈 줄(공백만 있는 줄 포함)은 오류로 치지 않고 조용히 건너뛴다.
    """
    orders = []
    errors = []

    for num_line, line in enumerate(lines, 1):
        if not line.strip():
            continue

        try:
            order = parse_order(line, sep=sep)
            orders.append(order)
        except ValueError as e:
            errors.append({"line": num_line, "reason": str(e)})

    return {"orders": orders, "errors": errors}
