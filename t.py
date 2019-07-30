def p(c):
    for j in c:
        print(j.n, end=' ')
    print(' ')


class A:
    def __init__(self, n):
        self.n = n


l = []
k = []
for i in range(5):
    if i == 2 or i == 3:
        k.append(A(i))
    l.append(A(i))

p(l)
p(k)
print('after')
for e in l:
    for ek in k:
        if e.n == ek.n:
            l.remove(e)
            print(e)
p(l)
p(k)





