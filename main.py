import time
from boop import Boop
from boopcli import BoopCLI
from bms import BiasedMaxSearcher, biasedEvaluate
from gameutil import elaborateState

boardDisplay = None

boardDisplay = """ _ _ _ _ _ _
|O|x|_|_|_|X|
|_|_|_|_|O|_|
|_|_|X|_|_|_|
|X|_|_|_|_|_|
|_|_|O|_|_|_|
|_|_|_|_|_|_|
 T T T T T T
P0: K1 C4
P1: K0 C4
Current player: 1
Place"""

def main():
    game = Boop(boardDisplay)
    def aiMove(game):
        ts = time.time()
        evaluation = BiasedMaxSearcher(game, max_workers=16).evaluateMoves(depth=4, traceChildren=True, parallel=True)
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
