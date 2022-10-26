import sys

# sys.setrecursionlimit(30000)


def test(n):
    if n != 0:
        n -= 1
        test(n)


if __name__ == "__main__":
    a = 65 / 1500
    print(a)
    b = a / (1 - a * 12)
    c = 0.0065 * 0.4 + 3.09027 * 0.6
    print(b)
    print(c)
