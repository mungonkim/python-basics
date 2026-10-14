"""2주차 문제 A 테스트. 위쪽 테스트는 고치지 않는다 (문제지 역할).

실행: uv run pytest week2 -v -k greet
"""

import pytest
from greet import greet


def test_greet_normal():
    assert greet("파이썬") == "안녕, 파이썬!"


def test_greet_strips_spaces():
    assert greet("  철수 ") == "안녕, 철수!"


def test_greet_only_spaces_raises():
    with pytest.raises(ValueError, match="이름"):
        greet("   ")


def test_greet_tab_and_newline_raises():
    with pytest.raises(ValueError, match="이름"):
        greet("\t\n")


# 직접 쓸 테스트: 빈 문자열("")을 넣었을 때 정한 결과를 확인한다.
def test_greet_empty_string_raises():
    with pytest.raises(ValueError, match="이름"):
        greet("")
