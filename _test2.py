import numpy as np
import cupy as cp
import time

def calculate_score_differences_2d(computeLib, playerCount: int, scoresArr):
    if playerCount <= 1:
        return computeLib.zeros_like(scoresArr)
    total_sums = computeLib.sum(scoresArr, axis=1)
    sum_excluding_self = total_sums[:, computeLib.newaxis] - scoresArr
    mean_excluding_self = sum_excluding_self / (playerCount - 1)
    result = scoresArr - mean_excluding_self
    return result

def calculate_score_differences_2d_2p(computeLib, scoresArr):
    total_sums = computeLib.sum(scoresArr, axis=1)
    result = scoresArr * 2 - total_sums[:, computeLib.newaxis]
    return result

# Custom kernel for playerCount = 2
# score_diff_kernel = cp.ElementwiseKernel(
#     in_params='float32 s0, float32 s1',
#     out_params='float32 r0, float32 r1',
#     operation='''
#         r0 = s0 - s1;  // s0 - (s1 / (2-1))
#         r1 = s1 - s0;  // s1 - (s0 / (2-1))
#     ''',
#     name='score_diff_kernel'
# )

def buildBiasedEvaluateKernel(playerCount):
    # FIXME: support playerCount > 2
    assert(playerCount == 2)
    in_params = ", ".join([f"float32 s{i}" for i in range(playerCount)]) # float32 s0, float32 s1
    out_params = ", ".join([f"float32 r{i}" for i in range(playerCount)]) # float32 r0, float32 r1
    if playerCount == 2:
        operation='''
            r0 = s0 - s1;
            r1 = s1 - s0;
        '''
    else:
        # FIXME:
        pass
    biasedEvaluateKernal = cp.ElementwiseKernel(
        in_params = in_params,
        out_params = out_params,
        operation = operation,
        name = f"biased_evaluation_kernal_p{playerCount}"
    )
    return biasedEvaluateKernal

def biasedEvaluate(biasedEvaluateKernal, playerCount, scoresArr):
    inParams = [scoresArr[:, i] for i in range(playerCount)]
    result = cp.empty_like(scoresArr)
    outParams = [result[:, i] for i in range(playerCount)]
    biasedEvaluateKernal(*inParams, *outParams)
    return result

# def calculate_score_differences_2d_custom(scoresArr):
#     # scoresArr: shape [num_sets, 2]
#     assert scoresArr.shape[1] == 2, "Custom kernel requires playerCount = 2"
#     # Initialize output array
#     result = cp.empty_like(scoresArr)
#     # Run kernel
#     score_diff_kernel(scoresArr[:, 0], scoresArr[:, 1], result[:, 0], result[:, 1])
#     return result

# Example usage
if __name__ == "__main__":
    # Simulate large input
    num_sets = 200000000
    playerCount = 2
    npArr = np.random.random((num_sets, playerCount)).astype(np.float32)
    
    # Warm-up GPU
    cp.sum(cp.array([1.0], dtype=cp.float32))
    cp.cuda.Stream.null.synchronize()
    print("Init complete")

    # CPU (NumPy)
    start_time = time.time()
    np_result = calculate_score_differences_2d(np, playerCount, npArr)
    cpu_time = time.time() - start_time
    print(f"CPU time: {cpu_time:.4f} seconds")

    start_time = time.time()
    np_result2 = calculate_score_differences_2d_2p(np, npArr)
    cp.cuda.Stream.null.synchronize()
    gpu_time = time.time() - start_time
    print(f"CPU time (2p): {gpu_time:.4f} seconds")
    
    # GPU (Original CuPy)
    start_time = time.time()
    cpArr = cp.array(npArr) # also consider the time of fetching data
    cp_result = calculate_score_differences_2d(cp, playerCount, cpArr)
    cp.cuda.Stream.null.synchronize()
    gpu_time = time.time() - start_time
    print(f"GPU time (original): {gpu_time:.4f} seconds")

    start_time = time.time()
    cpArr = cp.array(npArr) # also consider the time of fetching data
    cp_result2 = calculate_score_differences_2d_2p(cp, cpArr)
    cp.cuda.Stream.null.synchronize()
    gpu_time = time.time() - start_time
    print(f"GPU time (original 2p): {gpu_time:.4f} seconds")
    
    # GPU (Custom Kernel)
    kernal = buildBiasedEvaluateKernel(2)
    start_time = time.time()
    cpArr = cp.array(npArr) # also consider the time of fetching data
    # cp_result_custom = calculate_score_differences_2d_custom(cpArr)
    cp_result_custom = biasedEvaluate(kernal, 2, cpArr)
    cp.cuda.Stream.null.synchronize()
    gpu_time_custom = time.time() - start_time
    print(f"GPU time (custom kernel): {gpu_time_custom:.4f} seconds")

    print("Result shape:", cp_result_custom.shape)
    print("Sample result:", cp_result_custom[:5].get())
    
    # Verify results
    np.testing.assert_almost_equal(cp.asnumpy(np_result2), np_result, decimal=5)
    np.testing.assert_almost_equal(cp.asnumpy(cp_result), np_result, decimal=5)
    np.testing.assert_almost_equal(cp.asnumpy(cp_result2), np_result, decimal=5)
    np.testing.assert_almost_equal(cp.asnumpy(cp_result_custom), np_result, decimal=5)
    print("Results match between NumPy, CuPy, and Custom Kernel")