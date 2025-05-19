import numpy as np

import time

def sieve_prime(n:int):
    bound = int(np.sqrt(n) + 1)
    primes = np.full(n, 1, dtype=np.uint32)
    primes[0], primes[1] = 0, 0
    start = time.perf_counter()
    for i in range(bound):
        if i < primes.size:
            if primes[i] == 1:
                primes[i * i :: i] = 0
    print("time:", time.perf_counter() - start)
    #
    start = time.perf_counter()
    result = np.flatnonzero(primes)
    print("Result delivery time:", time.perf_counter() - start)
    return result

result = sieve_prime(1_000_000_000)
print(result)
print(len(result))
