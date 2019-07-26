import pickle

class B:
    def __init__(self, a_list):
        self.b = 2
        self.obj = a_list

class A:
    def __init__(self, b):
        self.a = 1
        self.object = b

b1 = B([])
a1 = A(b1)
pb1 = pickle.dumps(b1)
pb2 = pickle.dumps(a1)

print(type(pb1))