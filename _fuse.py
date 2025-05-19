import numpy as np
import cupy as cp
import time

@cp.fuse()
def saxpy(a, x, y):
    return a * x + y + x / a + a * y

def main():
    # Note: gpu run much faster for all cases
    # batchSize = 1024 * 2
    # size = 2**16
    # batchSize = 2**16
    # size = 1024 * 2
    batchSize = 1
    size = 1024 * 2 * 2**16

    a = np.float32(2.0)
    x = np.ones((batchSize, size), dtype=np.uint32)
    y = np.ones((batchSize, size), dtype=np.uint32)

    gx = cp.array(x, dtype=cp.uint32)
    gy = cp.array(y, dtype=cp.uint32)

    # warm up gpu
    cp.sum(cp.array([1], dtype=cp.uint32))
    cp.cuda.Stream.null.synchronize()

    #
    ts = time.perf_counter()
    result = a * x + y + x / a + a * y
    print("cpu time", time.perf_counter() - ts)
    print(result.shape)

    #
    ts = time.perf_counter()
    gresult = saxpy(a, gx, gy)
    cp.cuda.Stream.null.synchronize()
    print("gpu time", time.perf_counter() - ts)
    gresult = cp.asnumpy(gresult)
    print("gpu time", time.perf_counter() - ts)

    #
    ts = time.perf_counter()
    gresult = saxpy(a, gx, gy)
    cp.cuda.Stream.null.synchronize()
    print("gpu time 2", time.perf_counter() - ts)
    gresult = cp.asnumpy(gresult)
    print("gpu time 2", time.perf_counter() - ts)

    # verify
    np.testing.assert_almost_equal(gresult, result)
    print("verified")

main()
