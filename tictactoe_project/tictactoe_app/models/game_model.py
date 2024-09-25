from django.db import models
from .user_model import TicTacToeUser

class Game(models.Model):
    """
    Game model represents a single Tic Tac Toe game session played by a user.

    Attributes:
        player (ForeignKey): A reference to the TicTacToeUser who played the game.
        game_id (AutoField): A unique identifier for each game, automatically incremented.
        player_symbol (CharField): The symbol used by the player, default is 'X'.
        ai_symbol (CharField): The symbol used by the AI opponent, default is 'O'.
        date (DateTimeField): The date and time when the game was created, automatically set to the current timestamp.
        completed (BooleanField): A boolean indicating whether the game has been completed.
        winner (CharField): Indicates the winner of the game, can be 'X', 'O', or None (if it's a draw or ongoing).

    Methods:
        __str__(): Returns a string representation of the game, including the game ID and the player's username.
        get_moves(): Retrieves all the moves made during this game in the order of their turn number.

    Related Models:
        GameLog: Represents each move made in a game, linked through a ForeignKey relationship.
    """

    # Foreign key relationship to the TicTacToeUser who played the game.
    player = models.ForeignKey(TicTacToeUser, on_delete=models.CASCADE)

    # Unique identifier for each game, automatically incrementing.
    game_id = models.AutoField(primary_key=True)

    # The symbol used by the player ('X' by default).
    player_symbol = models.CharField(max_length=1, default='X')

    # The symbol used by the AI ('O' by default).
    ai_symbol = models.CharField(max_length=1, default='O')

    # The date and time when the game was created.
    date = models.DateTimeField(auto_now_add=True)

    # Boolean field to indicate if the game is completed or still ongoing.
    completed = models.BooleanField(default=False)

    # Indicates the winner of the game ('X', 'O', or None).
    winner = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        """
        Provides a human-readable representation of the Game instance.

        Returns:
            str: A string that includes the game ID and the username of the player.
        """
        return f"Game {self.game_id} - {self.player.username}"

    def get_moves(self):
        """
        Retrieves all the moves made in this game in the order they were played.

        The method queries the related GameLog entries, orders them by the turn number, and
        returns them as a list of dictionaries for each move.

        Returns:
            list: A list of dictionaries, each representing a move in the game with keys:
                  'turn_number' (int), 'player' (str), 'cell' (str), 'timestamp' (str).
        """
        # Retrieve the GameLog entries related to this game, ordered by turn number
        game_logs = self.logs.order_by('turn_number')  # 'logs' is the reverse related name from GameLog

        # Convert each GameLog entry to a dictionary for easy handling
        moves = [{
            'turn_number': log.turn_number,
            'player': log.player,
            'cell': log.cell,
            'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for log in game_logs]

        return moves

class GameLog(models.Model):
    """
    GameLog model represents an individual move made in a Tic Tac Toe game.

    Attributes:
        game (ForeignKey): Reference to the Game this log entry is associated with.
        turn_number (IntegerField): The turn number of the move within the game (1-9).
        player (CharField): The symbol of the player who made the move ('X' or 'O').
        cell (CharField): The cell position (1-9) where the move was made.
        timestamp (DateTimeField): The date and time when the move was made, automatically set.

    Meta:
        indexes (list): Specifies indexing on the 'game' and 'turn_number' fields to optimize queries.

    Methods:
        __str__(): Returns a string representation of the move, including game ID, turn number, player symbol, and cell.
    """

    # Foreign key relationship to the Game this move belongs to.
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='logs')

    # The turn number for this move within the game (1-9).
    turn_number = models.IntegerField()

    # The player who made the move ('X' or 'O').
    player = models.CharField(max_length=1)

    # The cell where the move was made (1-9 representing the 3x3 board).
    cell = models.CharField(max_length=1)

    # The timestamp when the move was made, automatically set to the current date and time.
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Define an index to optimize querying for moves by game and turn number.
        indexes = [
            models.Index(fields=['game', 'turn_number']),
        ]
    
    def __str__(self):
        """
        Provides a human-readable representation of the GameLog instance.

        Returns:
            str: A string that includes the game ID, turn number, player symbol, and cell played.
        """
        return f"Game {self.game.game_id} - Turn {self.turn_number} - {self.player} played {self.cell}"