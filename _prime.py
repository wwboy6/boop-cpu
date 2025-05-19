import cupy as cp

from numba import cuda

import time

BLOCK_SIZE = 1

@cuda.jit("void(uint32[:], int32)", cache=True)
def _sieve_forward(arr, bound) -> None:
    i = cuda.grid(1)
    if i < bound:
        if arr[i] == 1:
            arr[i * i :: i] = 0

def sieve_prime(n:int):
    bound = int(cp.sqrt(n) + 1)
    grid_blocks = (bound + (BLOCK_SIZE - 1)) // BLOCK_SIZE
    print("blocks:", grid_blocks)
    # warm up gpu
    cp.sum(cp.array([1], dtype=cp.uint32))
    cp.cuda.Stream.null.synchronize()
    #
    primes = cp.full(n, 1, dtype=cp.uint32)
    primes[0], primes[1] = 0, 0
    start = time.perf_counter()
    with cuda.defer_cleanup():
        _sieve_forward[grid_blocks, BLOCK_SIZE](primes, bound)
    # cp.cuda.Stream.null.synchronize()
    cuda.synchronize()
    print("time:", time.perf_counter() - start)
    #
    start = time.perf_counter()
    result = cp.flatnonzero(primes)
    print("Result delivery time:", time.perf_counter() - start)
    return result

result = sieve_prime(1_000_000_000)
print(result)
print(len(result))
