import numpy as np
from enum import Enum
import re

# Precompute connections once
def boop_setup(cls):
    connections = []
    directions = [
        [(0, 0), (1, 0), (2, 0)],  # right
        [(0, 0), (1, 1), (2, 2)],  # right bottom
        [(0, 0), (0, 1), (0, 2)],  # bottom
        [(0, 0), (-1, 1), (-2, 2)],  # left bottom
    ]
    for x in range(cls.boardSize):
        for y in range(cls.boardSize):
            for dir in directions:
                connection = [(x + dx, y + dy) for dx, dy in dir]
                if all(0 <= pos[0] < cls.boardSize and 0 <= pos[1] < cls.boardSize for pos in connection):
                    connections.append(tuple(connection))
    connections = np.array(connections, dtype="int")
    cls.connections = connections
    cls.allPositions = [(x, y) for x in range(cls.boardSize) for y in range(cls.boardSize)]
    # for checking if player can immediately win
    # data structure [[2d_pos0, 2d_pos1, ...], [2d_empty_pos0, 2d_empty_pos1, ...], 2d_win_pos]
    # the immediate winning loggic would check if all 2d_pos has current player's cats,
    # and all 2d_empty_pos and 2d_win_pos are empty
    # 2d_win_pos would be the placement of cat to be immediately win
    # win by 2 nearby cats with an available spot
    wpp = [[[c[0], c[1]], [], c[2]] for c in connections]
    if __name__ == "__main__": print(f"wpp {wpp[0]}")
    cls.winningPatterns = wpp
    wpp = [[[c[1], c[2]], [], c[0]] for c in connections]
    if __name__ == "__main__": print(f"wpp {wpp[0]}")
    cls.winningPatterns.extend(wpp)
    # win by 2 cats in a single connection (not nearby), with a cat next to the middle spot, and an available spot to push that cat into it
    # direction from middle to third cat is perpendicular with the connection
    # mirror the direction of the connection along x=y => flip(c1-c0)
    # mirror the it again along y=0, x=0 => *[-1,1], *[1,-1]
    extractMiddle = [[[c[0], c[2]], c[1], np.flip(c[1] - c[0]) * [-1, 1]] for c in connections]
    extractMiddle.extend([[[c[0], c[2]], c[1], np.flip(c[1] - c[0]) * [1, -1]] for c in connections])
    wpp = [[[*em[0], em[1]+em[2]], [em[1]], em[1]+em[2]+em[2]] for em in extractMiddle]
    wpp = [p for p in wpp if not cls.isOutOfBoard(p[2])]
    if __name__ == "__main__": print(f"wpp {wpp[0]}, len {len(wpp)}")
    cls.winningPatterns.extend(wpp)
    if __name__ == "__main__": print(f"wp count {len(cls.winningPatterns)}")
    # winningPatterns would be indexed by first element of pos (2d_pos0) as winningPatternMap
    cls.winningPatternMap = dict()
    for p in cls.winningPatterns:
        pos0 = tuple(p[0][0])
        if not pos0 in cls.winningPatternMap:
            cls.winningPatternMap[pos0] = [p]
        else:
            cls.winningPatternMap[pos0].append(p)
    return cls

@boop_setup
class Boop:
    boardSize = 6
    stateEmpty = (2, 2)
    stateDisplays = np.array((("o", "O", "-"), ("x", "X", "-"), ("-", "-", " ")))
    connectionLength = 3
    initPieceCount = 8

    class PlayerState(Enum):
        PLAY_CAT = 0
        PROMOTE_CAT = 1
        FINISHED = 2

    @classmethod
    def isOutOfBoard(cls, pos):
        x, y = pos
        return x < 0 or x >= cls.boardSize or y < 0 or y >= cls.boardSize

    class Player:
        def __init__(self, player=None):
            if player == None:
                self.catCounts = [Boop.initPieceCount, 0]  # [kittens, cats]
            else:
                self.catCounts = player.catCounts.copy()
        def __repr__(self):
            return f"[bp c:{self.catCounts}]"

    def __init__(self, saveStr=None, game=None):
        # copy game
        if game != None:
            self.board = game.board.copy()
            self.players = [Boop.Player(game.players[i]) for i in range(2)]
            self.currentPlayer = game.currentPlayer
            self.playerState = game.playerState
            self.promotionOptions = game.promotionOptions.copy()
            self.winningPieces = game.winningPieces.copy()
            # TODO: i doubt the performance improvement of using empty_spaces, as it would be copied for every new step
            self.empty_spaces = game.empty_spaces.copy()
            # no need to copy caches like immediatelyWinningMove
            self.immediatelyWinningMove = None
            return
        #
        self.players = [Boop.Player(), Boop.Player()]
        self.promotionOptions = []
        self.winningPieces = np.array([])
        self.playerState = Boop.PlayerState.PLAY_CAT
        self.immediatelyWinningMove = None
        if saveStr == None:
            self.board = np.full((self.boardSize, self.boardSize, 2), 2, dtype="int8")
            self.currentPlayer = 0
            self.empty_spaces = list(Boop.allPositions)
        else:
            # load save
            sdl = list(self.stateDisplays.reshape((-1,)))
            lines = saveStr.split('\n')
            # parse map
            mapStr = [line.split('|')[1:7] for line in lines[1:7]]
            indexes = [[sdl.index(v) for v in line] for line in mapStr]
            self.board = np.array([[[ind//3, ind%3] for ind in line] for line in indexes])
            # parse tokens
            self.players[0].catCounts = [int(str) for str in re.findall(r"\d", lines[8])[1:3]]
            self.players[1].catCounts = [int(str) for str in re.findall(r"\d", lines[9])[1:3]]
            # parse current player
            self.currentPlayer = int(re.findall(r"\d", lines[10])[0]) - 1
            # parse state
            match re.search(r"\w+", lines[11])[0]:
                case "Place": self.playerState = Boop.PlayerState.PLAY_CAT
                case "Promotion":
                    self.playerState = Boop.PlayerState.PROMOTE_CAT
                    # compute promotionOptions
                    self.promotionOptions = self.getPromotionOptions()
            # compute empty_space
            self.empty_spaces = [pos for pos in Boop.allPositions if np.all(self.board[*pos] == self.stateEmpty)]

    def getPromotionOptions(self):
        allOptions = []
        player = self.players[self.currentPlayer]
        if player.catCounts == [0, 0]:
            allOptions.extend([(pos,) for pos in self.allPositions if self.board[pos][0] == self.currentPlayer and self.board[pos][1] == 0])
        for conn in self.connections:
            if all(self.board[pos[0], pos[1]][0] == self.currentPlayer for pos in conn):
                allOptions.append(tuple(conn))
        return allOptions

    def getWinningConnections(self):
        bcPositions = [(x, y) for x in range(self.boardSize) for y in range(self.boardSize) 
                       if self.board[x, y][0] == self.currentPlayer and self.board[x, y][1] == 1]
        if len(bcPositions) == self.initPieceCount:
            self.winningPieces = np.array(bcPositions)
        for conn in self.connections:
            if all(np.all(self.board[pos[0], pos[1]] == [self.currentPlayer, 1]) for pos in conn):
                self.winningPieces = np.unique(conn, axis=0)
        return self.winningPieces

    def playCat(self, x, y, isBig):
        # TODO: prohibit move that produce same game state as before ??
        player = self.players[self.currentPlayer]
        player.catCounts[isBig] -= 1
        self.empty_spaces.remove((x, y))
        self.board[x, y] = (self.currentPlayer, isBig)
        
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = x + dx, y + dy
                if self.isOutOfBoard((tx, ty)):
                    continue
                target = self.board[tx, ty]
                if target[0] == 2 or target[1] > isBig:
                    continue
                nx, ny = tx + dx, ty + dy
                if self.isOutOfBoard((nx, ny)):
                    self.players[target[0]].catCounts[target[1]] += 1
                    self.board[tx, ty] = self.stateEmpty
                    self.empty_spaces.append((tx, ty))
                elif self.board[nx, ny][0] == 2:
                    self.board[nx, ny] = target
                    self.board[tx, ty] = self.stateEmpty
                    self.empty_spaces.remove((nx, ny))
                    self.empty_spaces.append((tx, ty))
        self.checkNextState()

    def checkNextState(self):
        if len(self.getWinningConnections()) > 0:
            self.playerState = Boop.PlayerState.FINISHED
        else:
            self.promotionOptions = self.getPromotionOptions()
            if self.promotionOptions:
                self.playerState = Boop.PlayerState.PROMOTE_CAT
            else:
                self.currentPlayer = 1 - self.currentPlayer
                self.playerState = Boop.PlayerState.PLAY_CAT

    def promote(self, index):
        for pos in self.promotionOptions[index]:
            self.board[*pos] = self.stateEmpty
            self.empty_spaces.append(tuple(pos))
        self.players[self.currentPlayer].catCounts[1] += len(self.promotionOptions[index])
        self.currentPlayer = 1 - self.currentPlayer
        self.playerState = Boop.PlayerState.PLAY_CAT

    def displayBoardState(self):
        result = " _ _ _ _ _ _ \n"
        for row in self.board:
            line = "|".join([self.stateDisplays[*state] for state in row])
            result += f"|{line}|\n"
        result += " T T T T T T "
        return result

    def displayGameState(self):
        board = self.displayBoardState()
        players = "\n".join([f"P{i}: K{p.catCounts[0]} C{p.catCounts[1]}" for i, p in enumerate(self.players)])
        return f"{board}\n{players}"
    
    def __repr__(self):
        return f"[Boop\n{self.displayBoardState()}\nps:{self.players} cp:{self.currentPlayer} s:{self.playerState}\nprom:{self.promotionOptions}\nwp:{self.winningPieces}]"

    def getPlayerCount(self) -> int:
        return 2

    def getCurrentPlayer(self) -> int:
        return self.currentPlayer
    
    # check if current player can win by actions without any other factor
    # return the next action to win
    def checkImmediatelyWin(self) -> any:
        # return None
        # current player need cat to win on next move
        if self.players[self.currentPlayer].catCounts[1] == 0: return None
        # return cache if any
        if self.immediatelyWinningMove != None: return self.immediatelyWinningMove
        # filter pattern
        currentPlayerCat = (self.currentPlayer, 1)
        # find pattern with matching cat
        pattern = None
        # search for cat and find potential patterns in winningPatternMap
        for pos in [pos for pos in self.allPositions if np.all(self.board[*pos] == currentPlayerCat)]:
            patterns = self.winningPatternMap[pos]
            for p in patterns:
                nextPattern = False
                for pos in p[0]:
                    if not np.all(self.board[*pos] == currentPlayerCat):
                        nextPattern = True
                        break
                if nextPattern: continue
                for pos in p[1]:
                    if not np.all(self.board[*pos] == self.stateEmpty):
                        nextPattern = True
                        break
                if nextPattern: continue
                if not np.all(self.board[*p[2]] == self.stateEmpty): continue
                pattern = p
                break
                # if np.all([np.all(self.board[*pos] == currentPlayerCat) for pos in p[0]]) and np.all([np.all(self.board[*pos] == self.stateEmpty) for pos in [*p[1], p[2]]]):
                #     pattern = p
                #     break
            if pattern: break
        if pattern:
            self.immediatelyWinningMove = ("playCat", [*pattern[2], 1])
        return self.immediatelyWinningMove

    def getPossibleMoves(self) -> list:
        # TODO: pioritize moves
        if self.playerState == Boop.PlayerState.PLAY_CAT:
            player = self.players[self.currentPlayer]
            moves = []
            if player.catCounts[0]:
                moves.extend(("playCat", (x, y, 0)) for x, y in self.empty_spaces)
            if player.catCounts[1]:
                moves.extend(("playCat", (x, y, 1)) for x, y in self.empty_spaces)
            return moves
        elif self.playerState == Boop.PlayerState.PROMOTE_CAT:
            return [("promoteCat", i) for i in range(len(self.promotionOptions))]
        # TODO: prohibit move that produce same game state as before ??
        return []
    
    # this is faster than copy.deepcopy
    def copy(self) -> 'Boop':
        return Boop(game=self)

    def makeMove(self, move) -> 'Boop':
        action, value = move
        if action == "playCat":
            self.playCat(*value)
        elif action == "promoteCat":
            self.promote(value)
        return self

    def isCompleted(self) -> bool:
        return self.playerState == Boop.PlayerState.FINISHED

    def evaluate(self) -> list[float]:
        # TODO: cache in case it would be called more than once
        return [self.evaluatePlayer(i) for i in range(2)]

    evalScoreReserveKitten = 0
    evalScoreBoardKitten = 100
    evalScoreReserveCat = 400 # upgrading 3 kitten in the center of board = (400-100)*3-4-4-3 = 889 >>> removing 1 kitten / cat on edge
    evalScoreBoardCat = 495 # score loss of removing kitten on edge is more than removing cat
    # FIXME: promoting 1 kitten with 2 cats = 300 - 101*2 = 98
    evalScoreBoardPieceBonuses = np.array([
        [0, 1, 1, 1, 1, 0],
        [1, 2, 3, 3, 2, 1],
        [1, 3, 4, 4, 3, 1],
        [1, 3, 4, 4, 3, 1],
        [1, 2, 3, 3, 2, 1],
        [0, 1, 1, 1, 1, 0],
    ], dtype="int")
    evalScoreBoardPieceBonusesMul = [1, 2] # score gain of placing kitten in the center is more than placing cat
    # set a large value for winning
    evalScoreWin = (evalScoreBoardCat * (initPieceCount - 1) + 2*16 + evalScoreReserveCat) * 2
    evalScoreLose = 0

    def evaluatePlayer(self, playerIndex: int) -> float:
        # game end score
        # this happen only if opponent push player's cat to right position
        if self.playerState == self.PlayerState.FINISHED:
            return self.evalScoreWin if playerIndex == self.currentPlayer else self.evalScoreLose
        # FIXME: this approach is to check checkImmediatelyWin on evaluatePlayer only to avoid doing this in every step of searching
        # test if checking this in every step would have a better performance
        if self.checkImmediatelyWin() != None:
            if self.currentPlayer == playerIndex: return self.evalScoreWin
            else: return self.evalScoreLose
        score = 0
        # if the next move is to promote, increase score by promotion
        if self.currentPlayer == playerIndex:
            match self.playerState:
                case self.PlayerState.PROMOTE_CAT:
                    # find all possible promotion and add the highest score that can be increased
                    playerKitten = (playerIndex, 0)
                    kittenCountInOption = [len([p for p in opt if np.all(self.board[*p] == playerKitten)]) for opt in self.promotionOptions]
                    maxCount = np.max(kittenCountInOption)
                    scoreIncreasment = np.max([0, maxCount*(self.evalScoreReserveCat-self.evalScoreBoardKitten)-(3-maxCount)*(self.evalScoreBoardCat)])
                    score += scoreIncreasment

        player = self.players[playerIndex]
        rk, rc = player.catCounts
        score += rk * self.evalScoreReserveKitten + rc * self.evalScoreReserveCat
        for x in range(self.boardSize):
            for y in range(self.boardSize):
                piece = self.board[x, y]
                if piece[0] == playerIndex:
                    base = self.evalScoreBoardKitten if piece[1] == 0 else self.evalScoreBoardCat
                    score += base + self.evalScoreBoardPieceBonuses[x, y] * self.evalScoreBoardPieceBonusesMul[piece[1]]
        return score
