
class A:
    def __init__(self, n):
        self.n = n
l = []
for i in range(5):
    l.append(A(i))

a = l[2]
l.remove(a)
print(l)