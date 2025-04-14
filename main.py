from boop import Boop
from boopcli import BoopCLI
from bms import BiasedMaxSearcher, biasedEvaluate
from gameutil import elaborateState

boardDisplay = None

boardDisplay = """ _ _ _ _ _ _ 
| | | | | |x|
| |o| | | | |
| | | | | |o|
| | | | | | |
| | | | | | |
|x| | | | | |
 T T T T T T
P0: K3 C3
P1: K3 C3
Current player: 1
Place"""

# boardDisplay = """ _ _ _ _ _ _ 
# | | | | | |x|
# | |o| | | | |
# | | | | | |o|
# | | | | | | |
# | | | |x|x|x|
# |x| | | | | |
#  T T T T T T
# P0: K3 C3
# P1: K3 C0
# Current player: 2
# Promotion"""
# Place"""
# Promotion"""

def main():
    game = Boop(boardDisplay)
    def aiMove(game):
        evaluation = BiasedMaxSearcher(game).evaluateMoves(depth=4, traceChildren=True)
        if evaluation.children: # evaluation.children may not exist for shortcut
            print(f"vvvvvvvvvvvvvvvvvvvv")
            print(f"origin game state")
            print(game)
            elaborateState(game, evaluation)
            print(f"bs: {[biasedEvaluate(game, c.scores) for c in evaluation.children]}")
            print(f"^^^^^^^^^^^^^^^^^^^^")
        return evaluation.bestMove

    cli = BoopCLI(game, True, aiMove)
    cli.play()

if __name__ == "__main__":
    main()
