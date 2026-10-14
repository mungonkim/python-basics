"""1주차 파이썬 점검 문제.

각 함수의 설명(docstring)을 읽고 `raise NotImplementedError` 줄을 지운 뒤 직접 구현한다.
확인: uv run pytest week1 -v
"""

import re


# 문제 1. 문자열과 딕셔너리
def count_words(text):
    """문장 속 단어가 몇 번 나오는지 센다.

    - 대소문자는 구분하지 않는다 (모두 소문자로).
    - 마침표, 쉼표, 느낌표, 물음표(. , ! ?)는 지운다.
    - 단어는 공백으로 나눈다.
    예: count_words("Hi, hi! Bye.") -> {"hi": 2, "bye": 1}
    빈 문자열이면 빈 딕셔너리.
    """

    word = {}

    text = text.lower()
    text = re.sub(r"[\.,!?]", "", text)
    text = text.split()

    for i in text:
        if i in word:
            word[i] += 1
        else:
            word[i] = 1
    return word


# 문제 2. 정렬과 key
def top_n(counts, n=3):
    """단어별 횟수 딕셔너리에서 가장 많이 나온 단어 n개를 (단어, 횟수) 튜플 리스트로 돌려준다.

    - 횟수가 많은 순서. 횟수가 같으면 단어의 가나다(알파벳)순.
    - n의 기본값은 3. 단어가 n개보다 적으면 있는 만큼만.
    예: top_n({"b": 2, "a": 2, "c": 5}, 2) -> [("c", 5), ("a", 2)]
    """
    counts = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:n]

    return counts


# 문제 3. 리스트와 집합
def unique_in_order(items):
    """중복을 지우되, 처음 나온 순서는 그대로 둔다.

    예: unique_in_order([3, 1, 3, 2, 1]) -> [3, 1, 2]
    """
    items = list(dict.fromkeys(items))

    return items


# 문제 4. 컴프리헨션
def even_squares(numbers):
    """짝수만 골라 제곱한 리스트를 돌려준다. 한 줄 리스트 컴프리헨션으로 쓴다.

    예: even_squares([1, 2, 3, 4]) -> [4, 16]
    """
    return [i**2 for i in numbers if i % 2 == 0]


# 문제 5. 딕셔너리로 묶기
def group_by_category(products):
    """상품 목록을 카테고리별 상품 이름 리스트로 묶는다.

    products: [{"name": "사과", "category": "과일", "price": 1200}, ...]
    - 이름은 원래 순서대로.
    예: [{"name": "사과", "category": "과일", ...}, {"name": "우유", "category": "유제품", ...},
         {"name": "배", "category": "과일", ...}]
        -> {"과일": ["사과", "배"], "유제품": ["우유"]}
    """
    category = {}
    for item in products:
        cat = item["category"]
        name = item["name"]

        if cat not in category:
            category[cat] = []

        category[cat].append(name)

    return category


# 문제 6. 집계와 빈 값 처리
def summarize_prices(products):
    """상품 가격을 요약한다.

    돌려주는 값: {"count": 개수, "min": 최저가, "max": 최고가, "avg": 평균(소수 첫째 자리 반올림)}
    - 상품이 없으면 {"count": 0, "min": None, "max": None, "avg": None}
    예: 가격이 1000, 2000, 2500 -> {"count": 3, "min": 1000, "max": 2500, "avg": 1833.3}
    """

    if not products:
        return {"count": 0, "min": None, "max": None, "avg": None}

    prices = [p["price"] for p in products]

    # 3. 집계 연산 및 반올림 처리
    return {
        "count": len(prices),
        "min": min(prices),
        "max": max(prices),
        "avg": round(sum(prices) / len(prices), 1),  # 소수점 첫째 자리까지 반올림
    }


# 문제 7. 문자열 파싱과 기본값 인자
def parse_order(line, sep=","):
    """주문 한 줄을 딕셔너리로 바꾼다.

    line 형식: "날짜{sep}상품{sep}수량{sep}단가"  예: "2026-10-14,사과,3,1200"
    - 앞뒤 공백은 지운다 (각 칸마다).
    - 수량과 단가는 int로, total = 수량 x 단가.
    예: parse_order("2026-10-14, 사과 ,3,1200")
        -> {"date": "2026-10-14", "item": "사과", "qty": 3, "price": 1200, "total": 3600}
    sep를 바꿀 수 있다: parse_order("2026-10-14|우유|1|2500", sep="|")
    """
    parts = line.split(sep)

    date = parts[0].strip()
    item = parts[1].strip()
    qty = int(parts[2].strip())
    price = int(parts[3].strip())

    return {
        "date": date,
        "item": item,
        "qty": qty,
        "price": price,
        "total": qty * price,
    }


# 문제 8. 슬라이싱과 반복
def chunk(items, size=2):
    """리스트를 size개씩 나눈다. 마지막 묶음은 모자라도 그대로 둔다.

    예: chunk([1, 2, 3, 4, 5], 2) -> [[1, 2], [3, 4], [5]]
    빈 리스트면 [].
    """

    result = []

    for i in range(0, len(items), size):
        result.append(items[i : i + size])

    return result
