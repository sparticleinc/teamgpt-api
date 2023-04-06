import random


def number(self, length: int = 6) -> str:
    digits = list(range(10))
    code = ''.join(map(str, random.sample(digits, length)))
    return code
