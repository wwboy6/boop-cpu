import concurrent.futures
import multiprocessing
from typing import Any
from math import nan

from game import Game

def biasedEvaluate(game: Game, scores: list[float]) -> float:
    playerCount, currentPlayer = game.getPlayerCount(), game.getCurrentPlayer()
    result = scores[currentPlayer] - sum(v for i, v in enumerate(scores) if i != currentPlayer) / (playerCount - 1)
    return result

class BiasedMaxSearcher:
    def __init__(self, game: Game, max_workers = 8):
        self.game = game
        self.max_workers = max_workers

    class Evaluation:
        # TODO: add game
        def __init__(self, currentMove, scores, bestMove, children, childIndex):
            self.currentMove = currentMove
            self.scores = scores
            self.bestMove = bestMove
            self.children = children
            self.childIndex = childIndex

    # return: (scores, nextMove, children, choosenIndex)
    def evaluateMoves(self, depth=3, traceChildren=False, game=None, parallel=True) -> Evaluation:
        if game is None:
            game = self.game
        with multiprocessing.Manager() as manager:
            self.cache = manager.dict()
            result = self._evaluateMoves(depth, traceChildren, game, None, parallel, True)
        self.cache = None
        return result

    def _evaluateMoves(self, depth, traceChildren, game, currentMove, parallel=False, isTopLevel=False) -> Evaluation:
        # Cache key based on game state
        state_key = (depth, game.currentPlayer, game.playerState.value, tuple(map(tuple, game.board.reshape(-1, 2))))

        if state_key in self.cache:
            return self.cache[state_key]
        
        # TODO: check cache in progress
        # if the cache is in progress, suspend the evaluation and check it again later

        if game.isCompleted():
            result = self.Evaluation(currentMove, game.evaluate(), None, None, nan)
            if not state_key in self.cache: self.cache[state_key] = result
            return result
        
        moves = None
        # shortcut searching for winning
        winningMove = game.checkImmediatelyWin()
        if winningMove != None:
            moves = [winningMove]
        else:
            moves = game.getPossibleMoves()

        if not moves:
            # game.getPossibleMoves should return at least one move. Even pass turn should be a move
            raise Exception("no move is available")
        
        # shortcut for only 1 move
        if isTopLevel and len(moves) == 1:
            return self.Evaluation(None, None, moves[0], None, nan)
        
        # TODO: check some of moves instead of every moves to reduce workload, but how to choose move?

        if depth == 1:
            # At depth 1, evaluate moves directly (no need for threading here)
            evaluations = [self.Evaluation(m, game.copy().makeMove(m).evaluate(), None, None, nan) for m in moves]
        else:
            # TODO: dynamic thread allocation: check available thread (cpu core) can be obtained and create new executor w.r.t. that number
            # with a max thread limit per tree layer, say 1 for first layer and 3 other layer
            # when a sub-search using executor is completed, release the available thread count
            if parallel and len(moves) > 1:
                # Use multi-threading for deeper evaluations
                evaluations = self._evaluate_moves_parallel(moves, depth - 1, traceChildren, game)
            else:
                evaluations = [self._evaluate_move(m, depth - 1, traceChildren, game) for m in moves]

        # Sort by biased evaluation
        biased_evals = sorted([(biasedEvaluate(game, ev.scores), ev) for ev in evaluations], key=lambda x: x[0], reverse=True)
        # TODO: handle more than 1 best choice
        bestIndex = 0
        best_eval = biased_evals[bestIndex][1]
        # trace children
        if traceChildren:
            result = self.Evaluation(currentMove, best_eval.scores, best_eval.currentMove, [ev[1] for ev in biased_evals], bestIndex)
        else:
            result = self.Evaluation(currentMove, best_eval.scores, best_eval.currentMove, None, nan)

        if not state_key in self.cache: self.cache[state_key] = result
        return result

    def _evaluate_move(self, move, depth, traceChildren, game):
        """Helper function to evaluate a single move (used in threading)."""
        next_game = game.copy().makeMove(move)
        return self._evaluateMoves(depth, traceChildren, next_game, move)

    def _evaluate_moves_parallel(self, moves, depth, traceChildren, game):
        """Evaluates all moves in parallel using ProcessPoolExecutor."""
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all move evaluations to the thread pool
            future_to_move = {executor.submit(self._evaluate_move, move, depth, traceChildren, game): move for move in moves}
            # Collect results as they complete
            evaluations = [future.result() for future in concurrent.futures.as_completed(future_to_move)]
        return evaluations
