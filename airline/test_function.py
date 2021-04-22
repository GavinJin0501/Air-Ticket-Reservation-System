import re
EMAIL_REGEX = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


def is_math(stdin, pattern):
    return re.search(pattern, stdin) is not None


while True:
    s = input(("What is your email: "))
    print(is_math(s, EMAIL_REGEX))