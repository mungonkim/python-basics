"""2주차 1일차 문제 A. 예외 처리로 잘못된 이름 막기.

함수 설명(docstring)을 읽고 `raise NotImplementedError` 줄을 지운 뒤 직접 구현한다.
확인: uv run pytest week2 -v -k greet
직접 실행: uv run python week2/greet.py
"""


def greet(name):
    """이름을 받아 인사말을 돌려준다.

    - 이름 앞뒤 공백은 지운다: greet("  철수 ") -> "안녕, 철수!"
    - 공백만 있는 이름("   ", "\t\n")이면 ValueError를 낸다. 메시지에 "이름"이 들어가게 한다.
    - 빈 문자열("")은 어떻게 할지 직접 정한다 (0주차처럼 "안녕!" 또는 ValueError).
      정한 대로 test_greet.py 맨 아래에 테스트를 직접 하나 추가한다.
    """
    name = name.strip()

    if name:
        return f"안녕, {name}!"
    else:
        raise ValueError("올바른 이름을 입력하세요")


if __name__ == "__main__":
    # 여기에 input() + while + try/except로 "제대로 된 이름이 들어올 때까지 다시 묻기"를 쓴다.
    # 잘못 입력하면 다시 입력하라는 안내를 출력한다.

    while True:
        try:
            name = input("이름을 입력하세요.")
            message = greet(name)
            print(message)
            break
        except ValueError as e:
            print(f"잘못입력하셨습니다. {e} 다시 시도하세요. \n")
