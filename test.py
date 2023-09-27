from typing import Counter
from math import log

for _ in range(int(input())):
    n = int(input())
    a = list(map(int, input().split()))
    l = [a]
    ceil = int(log(n, 2)) + 1
    for i in range(ceil):
        X = Counter(a)
        a = [X[i] for i in a]
        l.append(a)
    q = int(input())
    for i in range(q):
        x, k = list(map(int, input().split()))
        print(l[min(ceil, k)][x - 1])
