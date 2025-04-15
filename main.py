import time
from boop import Boop
from boopcli import BoopCLI
from bms import BiasedMaxSearcher, biasedEvaluate
from gameutil import elaborateState

boardDisplay = None

# boardDisplay = """ _ _ _ _ _ _
# | |x| | | | |
# |x| |x|x|o|o|
# | | | | | | |
# |x| |x| |o| |
# | | | | | | |
# | | | |o| | |
#  T T T T T T
# P0: K2 C3
# P1: K1 C0
# Current player: 1
# Place"""

def main():
    game = Boop(boardDisplay)
    def aiMove(game):
        ts = time.time()
        evaluation = BiasedMaxSearcher(game, max_workers=16).evaluateMoves(depth=3, traceChildren=True, parallel=True)
        if evaluation.children: # evaluation.children may not exist for shortcut
            print(f"vvvvvvvvvvvvvvvvvvvv")
            print(f"origin game state")
            print(game)
            elaborateState(game, evaluation)
            print(f"bs: {[float(biasedEvaluate(game, c.scores)) for c in evaluation.children[:5]]}")
            print(f"^^^^^^^^^^^^^^^^^^^^")
        print(f"time: {time.time() - ts}")
        # TODO: make move as a class instance and implement __repr__
        print(f"AI move: {Boop.describeMove(evaluation.bestMove)}")
        return evaluation.bestMove

    cli = BoopCLI(game, True, aiMove)
    cli.play()

if __name__ == "__main__":
    main()
