"""2주차 4일차. HTTP와 httpx로 공개 API 호출하기.

Open-Meteo 날씨 API(키 없음, 무료)로 현재 기온과 바람을 가져온다.
- 함수 설명(docstring)을 읽고 `raise NotImplementedError` 줄을 지운 뒤 직접 구현한다.
- 테스트는 진짜 인터넷 대신 가짜 서버(MockTransport)를 쓴다. 그래서 fetch_current는 client를 인자로 받는다.
- 이번에는 타입 힌트를 미리 붙여 두었다. 채운 코드도 mypy --strict를 통과해야 한다.
- 확인 1: uv run pytest week2 -v -k weather
- 확인 2: uv run mypy --strict week2/weather.py
- 직접 실행(진짜 API): uv run python week2/weather.py 37.57 126.98
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

import httpx

API_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_FIELDS = "temperature_2m,wind_speed_10m"


class WeatherError(Exception):
    """날씨를 가져오지 못했을 때 내는 오류. 원래 오류는 `raise ... from e`로 이어 붙인다."""


# 문제 E-1. 현재 날씨 클래스와 응답 읽기
@dataclass
class CurrentWeather:
    """현재 날씨 한 건.

    필드 세 개를 직접 적는다 (dataclass 필드 형식: `이름: 타입`).
    - time: 관측 시각 문자열 (예: "2026-10-28T11:15")
    - temperature: 기온, 실수
    - wind_speed: 풍속, 실수
    """

    time: str
    temperature: float
    wind_speed: float


def parse_current(data: dict[str, Any]) -> CurrentWeather:
    """API 응답 JSON(딕셔너리)에서 현재 날씨를 꺼낸다.

    응답 모양 (필요한 부분만):
        {"current": {"time": "2026-10-28T11:15", "temperature_2m": 7.6, "wind_speed_10m": 5.2}}
    - temperature와 wind_speed는 float으로 바꿔 저장한다 (API가 8처럼 정수로 줄 때도 있다).
    - 필요한 키가 하나라도 없으면 WeatherError (메시지에 "형식").
    """

    try:
        current = data["current"]

        time = current["time"]
        temperature = float(current["temperature_2m"])
        wind_speed = float(current["wind_speed_10m"])

    except KeyError as e:
        raise WeatherError("응답 형식이 올바르지 않습니다.") from e

    return CurrentWeather(
        time=time,
        temperature=temperature,
        wind_speed=wind_speed,
    )


# 문제 E-2. 요청 파라미터 만들기
def build_params(latitude: float, longitude: float) -> dict[str, str | float]:
    """Open-Meteo에 보낼 쿼리 파라미터 딕셔너리를 만든다.

    - 위도는 -90 ~ 90, 경도는 -180 ~ 180. 벗어나면 요청을 보내기 전에 ValueError
      (메시지에 "위도" / "경도"). 서버에 보내 봐야 400이 올 요청은 미리 막는다.
    - 돌려주는 값:
        {"latitude": 위도, "longitude": 경도, "current": CURRENT_FIELDS, "timezone": "Asia/Seoul"}
    """
    if latitude < -90 or latitude > 90:
        raise ValueError("위도 범위를 벗어났습니다.")
    if longitude < -180 or longitude > 180:
        raise ValueError("경도 범위를 벗어났습니다.")

    return {
        "latitude": latitude,
        "longitude": longitude,
        "current": CURRENT_FIELDS,
        "timezone": "Asia/Seoul",
    }


# 문제 E-3. 요청 보내고 실패를 WeatherError로 바꾸기
def fetch_current(
    client: httpx.Client, latitude: float, longitude: float, timeout: float = 5.0
) -> CurrentWeather:
    """client로 API_URL에 GET 요청을 보내 현재 날씨를 돌려준다.

    - 파라미터는 build_params로 만든다. 위도 · 경도가 틀린 ValueError는 바꾸지 않고 그대로 나가게 둔다.
    - timeout을 요청에 넘긴다.
    - 실패는 모두 WeatherError로 바꾸고, 원래 오류를 from으로 이어 붙인다. 메시지에 들어갈 단어:
      - 서버가 4xx로 답함 → "요청"
      - 서버가 5xx로 답함 → "서버"
      - 시간 초과 → "시간"
      - 그 밖에 답을 못 받음(연결 실패 등) → "연결"
      - 200인데 본문이 JSON이 아님 → "형식"
      - JSON인데 필요한 키가 없음 → "형식" (parse_current가 이미 처리한다)
    - except는 좁게 쓴다 (`except Exception` 금지). 개념 3의 오류 가족 그림을 참고한다.
    """

    params = build_params(latitude, longitude)

    try:
        r = client.get(API_URL, params=params, timeout=timeout)

        r.raise_for_status()

    except httpx.TimeoutException as e:
        raise WeatherError("시간 초과 오류") from e

    except httpx.HTTPStatusError as e:
        status_coude = e.response.status_code

        if 400 <= status_coude < 500:
            raise WeatherError("요청 오류") from e

        raise WeatherError("서버 오류") from e

    except httpx.RequestError as e:
        raise WeatherError("연결 실패") from e

    try:
        data = r.json()
    except ValueError as e:
        raise WeatherError("응답 형식 오류") from e

    return parse_current(data)


# 문제 E-4. 사람이 읽을 문장으로
def format_weather(weather: CurrentWeather) -> str:
    """예: "2026-10-28T11:15 기온 7.6°C, 바람 5.2km/h" """
    return f"{weather.time} 기온 {weather.temperature}°C, 바람 {weather.wind_speed}km/h"


# 문제 E-5. 명령줄 실행 (테스트 없음, 진짜 API로 직접 확인)
def main(argv: list[str]) -> int:
    """명령줄 실행용. 테스트는 없다. 직접 실행해서 확인한다.

    - 인자가 2개(위도, 경도)가 아니거나 숫자로 바꿀 수 없으면 사용법을 출력하고 2를 돌려준다.
    - 위도 · 경도 범위가 틀리면(ValueError) 한 줄 안내를 출력하고 2를 돌려준다.
    - httpx.Client()를 with 문으로 만들어 fetch_current에 넘긴다.
    - WeatherError면 "오류: ..." 한 줄을 출력하고 1을 돌려준다.
    - 성공하면 format_weather 결과를 출력하고 0을 돌려준다.
    """
    if len(argv) != 2:
        print("사용법: python weather.py 위도 경도")
        return 2

    try:
        latitude = float(argv[0])
        longitude = float(argv[1])
    except ValueError:
        print("사용법: python weather.py 위도 경도")
        return 2

    try:
        build_params(latitude, longitude)
    except ValueError as e:
        print(f"오류: {e}")
        return 2

    try:
        with httpx.Client() as client:
            weather = fetch_current(client, latitude, longitude)

        # 5. 날씨 결과 출력
        print(format_weather(weather))
        return 0

    except WeatherError as e:
        print(f"오류: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
