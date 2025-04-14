from typing import Protocol, Self

class Game(Protocol):

    def getPlayerCount(self) -> int: pass

    def getCurrentPlayer(self) -> int: pass

    # check if current player can win by actions without any other factor
    # return the next action to win
    # this can shortcut the searching for next best move
    def checkImmediatelyWin(self) -> any: pass

    def getPossibleMoves(self) -> list: pass

    # TODO: consider different results can be obtained by chance
    def makeMove(self, move) -> Self: pass

    def isCompleted(self) -> bool: pass

    def evaluate(self) -> list[float]: pass
