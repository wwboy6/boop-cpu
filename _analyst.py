import numpy as np
from boop import Boop
from bms import BiasedMaxSearcher, biasedEvaluate
from gameutil import elaborateState, countEndChild
import time

# boardDisplay = """ _ _ _ _ _ _ 
# | | | | | | |
# | | | | | | |
# | | | | | | |
# | | | |o| | |
# | | | | | | |
# | | | | | | |
#  T T T T T T
# P0: K7 C0
# P1: K8 C0
# Current player: 1
# Place"""

# boardDisplay = """ _ _ _ _ _ _ 
# | | | | | |x|
# | |o| | | | |
# | | | | | |o|
# | | | | | | |
# | | | | | | |
# |x| | | | | |
#  T T T T T T
# P0: K3 C3
# P1: K3 C3
# Current player: 1
# Place"""

boardDisplay = """ _ _ _ _ _ _ 
|O| | | | |O|
| | | |O| | |
| | | | | |O|
| |O| | | | |
| | | | | | |
| | |O| |O| |
 T T T T T T
P0: K3 C3
P1: K3 C3
Current player: 1
Place"""

# Place"""
# Promotion"""

def main():
    game = Boop(boardDisplay)

    ts = time.time()

    print(f"{game.checkImmediatelyWin()}")
    for _ in range(100000):
        game.checkImmediatelyWin()
    
    # evaluation = BiasedMaxSearcher(game).evaluateMoves(depth=3, traceChildren=True, parallel=True)

    print(f"time: {time.time() - ts}")

    # print(f"move {evaluation.bestMove}")
    # if evaluation.children:
    #     elaborateState(game, evaluation)
    #     print(f"score:{evaluation.scores} be:{biasedEvaluate(game, evaluation.scores)}")
    #     endChildCount = countEndChild(evaluation)
    #     print(f"endChildCount:{endChildCount}")
    
    # print("======================")
    # print("======================")
    # print("======================")
    # # comparing with target move
    # targetMove = ('playCat', (0, 4, 1))
    # childFilter = [np.all(c.currentMove == targetMove) for c in evaluation.children]
    # childIndex = childFilter.index(True)
    # child = evaluation.children[childIndex]
    # evaluation2 = BiasedMaxSearcher.Evaluation(None, child.scores, targetMove, evaluation.children, childIndex)
    # elaborateState(game, evaluation2)
    # print(f"score:{evaluation2.scores} be:{biasedEvaluate(game, evaluation2.scores)}")

if __name__ == '__main__': main()
