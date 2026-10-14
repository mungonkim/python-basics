from hello import greet


def test1():
    assert greet("철수") == "안녕, 철수!"


def test2():
    assert greet("") == "안녕!"
