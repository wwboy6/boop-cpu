import cupy as cp
from numba import cuda
import time

BLOCK_SIZE = 256  # Optimal for GPU occupancy

@cuda.jit("void(uint32[:], int32, int32)", cache=True)
def _sieve_forward(arr, n, bound):
    k = cuda.grid(1)  # Thread index corresponds to array index
    if k < n:
        if k < 2:  # Handle 0 and 1
            arr[k] = 0
            return
        # Check if k is a multiple of any i <= bound
        for i in range(2, bound):
            if arr[i] == 1:  # Only check prime i
                if k >= i * i and k % i == 0:
                    arr[k] = 0
                    return

def sieve_prime(n: int):
    bound = int(cp.sqrt(n) + 1)
    grid_blocks = (n + (BLOCK_SIZE - 1)) // BLOCK_SIZE
    print("blocks:", grid_blocks)
    
    # Warm up GPU
    cp.sum(cp.array([1], dtype=cp.uint32))
    
    # Initialize array
    primes = cp.full(n, 1, dtype=cp.uint32)
    start = time.perf_counter()
    with cuda.defer_cleanup():
        _sieve_forward[grid_blocks, BLOCK_SIZE](primes, n, bound)
    cp.cuda.Stream.null.synchronize()
    print("time:", time.perf_counter() - start)
    
    # Extract primes
    start = time.perf_counter()
    result = cp.flatnonzero(primes)
    print("Result delivery time:", time.perf_counter() - start)
    return result

result = sieve_prime(1_000_000_000)
print(len(result))