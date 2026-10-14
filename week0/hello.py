def greet(name):
    if name:
        return f"안녕, {name}!"
    return "안녕!"


if __name__ == "__main__":
    print(greet("파이썬"))
