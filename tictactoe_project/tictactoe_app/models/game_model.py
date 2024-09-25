from django.db import models
from .user_model import TicTacToeUser

class Game(models.Model):
    player = models.ForeignKey(TicTacToeUser, on_delete=models.CASCADE)  # The user who played the game
    game_id = models.AutoField(primary_key=True)  # Game ID auto-incrementing
    player_symbol = models.CharField(max_length=1, default='X')  # Player's symbol ('X')
    ai_symbol = models.CharField(max_length=1, default='O')  # AI's symbol ('O')
    date = models.DateTimeField(auto_now_add=True)  # The date the game was played
    completed = models.BooleanField(default=False)  # Whether the game is completed
    winner = models.CharField(max_length=1, blank=True, null=True)  # Winner ('X', 'O', or None)

    def __str__(self):
        return f"Game {self.game_id} - {self.player.username}"

    def get_moves(self):
        """
        Retrieve all the moves made during this game, ordered by turn number.
        
        Returns:
            list: A list of dictionaries representing the moves in the game.
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
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='logs')  # The game this log is part of
    turn_number = models.IntegerField()  # Turn number
    player = models.CharField(max_length=1)  # 'X' or 'O'
    cell = models.CharField(max_length=1)  # The cell played (1-9)
    timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of the move

    class Meta:
        indexes = [
            models.Index(fields=['game', 'turn_number']),  # Add index for faster querying
        ]
    
    def __str__(self):
        return f"Game {self.game.game_id} - Turn {self.turn_number} - {self.player} played {self.cell}"