import numpy as np
import cupy as cp
import time

def calculate_score_differences_2d(computeLib, playerCount: int, scoresArr):
    # Compute total sum for each score set (shape: [num_sets])
    total_sums = computeLib.sum(scoresArr, axis=1)
    # Broadcast total_sums to shape [num_sets, playerCount]
    # Subtract scoresArr to exclude each player's score
    sum_excluding_self = total_sums[:, computeLib.newaxis] - scoresArr
    # Compute mean of other players' scores
    mean_excluding_self = sum_excluding_self / (playerCount - 1)
    # Compute final result: scores - mean_excluding_self
    result = scoresArr - mean_excluding_self
    return result

# Example usage
if __name__ == "__main__":
    # Simulate large input
    num_sets = 90000000
    playerCount = 2
    # scoresArr = cp.random.random((num_sets, playerCount))
    # using float32
    npArr = np.random.random((num_sets, playerCount)).astype(np.float32)
    cpArr = cp.array(npArr)
    
    # Warm-up GPU
    cp.sum(cp.array([1.0], dtype=cp.float32))
    cp.cuda.Stream.null.synchronize()  # Ensure GPU computation is complete
    print(f"Init complete")

    start_time = time.time()
    np_result = calculate_score_differences_2d(np, playerCount, npArr)
    cpu_time = time.time() - start_time
    print(f"CPU time: {cpu_time:.4f} seconds")
    
    # Run optimized computation
    start_time = time.time()
    cp_result = calculate_score_differences_2d(cp, playerCount, cpArr)
    cp.cuda.Stream.null.synchronize()  # Ensure GPU computation is complete
    gpu_time = time.time() - start_time
    print(f"GPU time: {gpu_time:.4f} seconds")

    # print("Result shape:", cp_result.shape)
    # print("Sample result:", cp_result[:5, :5].get())  # Small sample for display
    
    # # Verify results
    # np.testing.assert_almost_equal(cp.asnumpy(cp_result), np_result, decimal=5)
    # print("Results match between NumPy and CuPy")
