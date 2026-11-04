"""2주차 4일차 테스트. 이 파일은 고치지 않는다 (문제지 역할).

진짜 인터넷에 나가지 않는다. 모든 요청은 가짜 서버(MockTransport)가 대신 답한다.
실행: uv run pytest week2 -v -k weather
"""

import json

import httpx
import pytest
from weather import (
    API_URL,
    CURRENT_FIELDS,
    CurrentWeather,
    WeatherError,
    build_params,
    fetch_current,
    format_weather,
    parse_current,
)

SAMPLE = {
    "latitude": 37.55,
    "longitude": 127.0,
    "current": {
        "time": "2026-10-28T11:15",
        "temperature_2m": 7.6,
        "wind_speed_10m": 5.2,
    },
}


def fake_client(handler):
    """handler(요청) → 응답 함수를 가짜 서버로 끼운 Client를 만든다."""
    return httpx.Client(transport=httpx.MockTransport(handler))


def answer(status, body=None, text=None):
    """항상 같은 응답을 주는 가짜 서버."""

    def handler(request):
        if text is not None:
            return httpx.Response(status, text=text)
        return httpx.Response(status, json=body)

    return fake_client(handler)


def fail_with(error_class):
    """요청할 때마다 error_class 오류를 내는 가짜 서버 (인터넷 끊김, 시간 초과 흉내)."""

    def handler(request):
        raise error_class("가짜 네트워크 오류", request=request)

    return fake_client(handler)


# 문제 E-1
def test_parse_current():
    weather = parse_current(SAMPLE)
    assert weather == CurrentWeather(
        time="2026-10-28T11:15", temperature=7.6, wind_speed=5.2
    )


def test_parse_current_converts_int_to_float():
    data = {"current": {"time": "t", "temperature_2m": 8, "wind_speed_10m": 0}}
    weather = parse_current(data)
    assert weather.temperature == 8.0
    assert isinstance(weather.temperature, float)
    assert isinstance(weather.wind_speed, float)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"current": {"time": "t", "temperature_2m": 7.6}},
    ],
)
def test_parse_current_missing_keys(data):
    with pytest.raises(WeatherError, match="형식"):
        parse_current(data)


# 문제 E-2
def test_build_params():
    assert build_params(37.57, 126.98) == {
        "latitude": 37.57,
        "longitude": 126.98,
        "current": CURRENT_FIELDS,
        "timezone": "Asia/Seoul",
    }


@pytest.mark.parametrize(
    ("latitude", "longitude", "word"),
    [
        (91, 0, "위도"),
        (-90.5, 0, "위도"),
        (0, 180.1, "경도"),
        (0, -181, "경도"),
    ],
)
def test_build_params_rejects_out_of_range(latitude, longitude, word):
    with pytest.raises(ValueError, match=word):
        build_params(latitude, longitude)


def test_build_params_accepts_edges():
    build_params(90, 180)
    build_params(-90, -180)


# 문제 E-3
def test_fetch_current_success():
    client = answer(200, SAMPLE)
    assert fetch_current(client, 37.57, 126.98) == CurrentWeather(
        "2026-10-28T11:15", 7.6, 5.2
    )


def test_fetch_current_sends_right_request():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=SAMPLE)

    fetch_current(fake_client(handler), 37.57, 126.98)

    request = seen[0]
    assert request.method == "GET"
    assert str(request.url).startswith(API_URL)
    assert request.url.params["latitude"] == "37.57"
    assert request.url.params["longitude"] == "126.98"
    assert request.url.params["current"] == CURRENT_FIELDS


def test_fetch_current_bad_coordinates_never_sends():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=SAMPLE)

    with pytest.raises(ValueError, match="위도"):
        fetch_current(fake_client(handler), 999, 126.98)
    assert seen == []


@pytest.mark.parametrize(
    ("status", "word"),
    [
        (400, "요청"),
        (404, "요청"),
        (500, "서버"),
        (503, "서버"),
    ],
)
def test_fetch_current_status_errors(status, word):
    client = answer(status, {"error": True, "reason": "가짜 오류"})
    with pytest.raises(WeatherError, match=word) as caught:
        fetch_current(client, 37.57, 126.98)
    assert isinstance(caught.value.__cause__, httpx.HTTPStatusError)


def test_fetch_current_timeout():
    with pytest.raises(WeatherError, match="시간") as caught:
        fetch_current(fail_with(httpx.ReadTimeout), 37.57, 126.98)
    assert isinstance(caught.value.__cause__, httpx.TimeoutException)


def test_fetch_current_connect_error():
    with pytest.raises(WeatherError, match="연결") as caught:
        fetch_current(fail_with(httpx.ConnectError), 37.57, 126.98)
    assert isinstance(caught.value.__cause__, httpx.ConnectError)


def test_fetch_current_not_json():
    client = answer(200, text="<html>점검 중</html>")
    with pytest.raises(WeatherError, match="형식") as caught:
        fetch_current(client, 37.57, 126.98)
    assert isinstance(caught.value.__cause__, json.JSONDecodeError)


def test_fetch_current_missing_keys():
    client = answer(200, {"latitude": 37.55})
    with pytest.raises(WeatherError, match="형식"):
        fetch_current(client, 37.57, 126.98)


# 문제 E-4
def test_format_weather():
    weather = CurrentWeather("2026-10-28T11:15", 7.6, 5.2)
    assert format_weather(weather) == "2026-10-28T11:15 기온 7.6°C, 바람 5.2km/h"
