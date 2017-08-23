from collections import deque

q = deque();
q.append("aa")
q.append("bb")
q.append("cc")
while q:
    print(q.popleft())
#print(q.pop())
#print(q.pop())
