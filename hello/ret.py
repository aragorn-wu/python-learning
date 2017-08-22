import re

class ret:
    def __init__(self):
        self.start = 0

    def hello(self):
        pattern=re.compile(r"hello")
        match=pattern.match('hello world,hello py')
        if match:
            print(match.group())

r=ret()
r.hello()