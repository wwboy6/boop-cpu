from boop import Boop

class BoopCLI:
    def __init__(self, game, hasBot = True, aiMove = None):
        self.game = game
        self.hasBot = hasBot
        self.aiMove = aiMove

    def get_user_move(self):
        """Prompts the user for a move based on the current game state and returns it."""
        if self.game.playerState == Boop.PlayerState.PLAY_CAT:
            return self._get_play_cat_move()
        elif self.game.playerState == Boop.PlayerState.PROMOTE_CAT:
            return self._get_promote_move()
        else:
            print("Game is finished!")
            return None

    def _get_play_cat_move(self):
        """Handles input for placing a cat on the board."""
        player = self.game.players[self.game.currentPlayer]
        
        while True:
            try:
                size = input("Place a kitten (0) or cat (1)? ").strip()
                if size not in ("0", "1") or player.catCounts[int(size)] <= 0:
                    print("Invalid size or no pieces available!")
                    continue
                
                y = int(input(f"Enter column (0-{Boop.boardSize-1}): "))
                x = int(input(f"Enter row (0-{Boop.boardSize-1}): "))
                if self.game.isOutOfBoard((x, y)) or tuple(self.game.board[x, y]) != Boop.stateEmpty:
                    print("Invalid position or space occupied!")
                    continue
                
                return ("playCat", (x, y, int(size)))
            except ValueError:
                print("Please enter valid numbers!")

    def _get_promote_move(self):
        """Handles input for promoting cats."""
        options = self.game.promotionOptions
        print("Promotion options:")
        for i, opt in enumerate(options):
            print(f"{i}: {opt}")
        
        while True:
            try:
                choice = int(input(f"Choose an option (0-{len(options)-1}): "))
                if 0 <= choice < len(options):
                    return ("promoteCat", choice)
                print("Invalid option!")
            except ValueError:
                print("Please enter a valid number!")

    def play(self):
        """Runs a simple game loop for user interaction."""
        if self.hasBot:
            # TODO: random first player
            playerControls = ( # (isHuman)
                (True),
                (False)
            )
        else:
            playerControls = ( # (isHuman)
                (True),
                (True)
            )
        print("\n")
        while not self.game.isCompleted():
            print(self.game.displayGameState())
            print(f"Current player: {self.game.currentPlayer + 1}")
            (isHuman) = playerControls[self.game.currentPlayer]
            if isHuman:
                move = self.get_user_move()
                if move:
                    self.game.makeMove(move)
            else:
                move = self.aiMove(self.game)
                print(f"AI move: {move}")
                self.game.makeMove(move)
        print(self.game.displayBoardState())
        print(f"Player {self.game.currentPlayer + 1} wins!")
