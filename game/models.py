from django.db import models
import re

class Game(models.Model):
    pass

class Board(models.Model):
    game = models.ForeignKey(Game)
    move_no = models.IntegerField()
    rows = models.IntegerField()
    columns = models.IntegerField()
    board = models.TextField()


class StandardBoard:
    rows = 11
    columns = 16

    G, T, R  = 'G','T', 'R'
    default_board = (G, G, G, G, R, R, R, R, R, G, T, G, R, G, G, G,
                     G, T, G, G, R, G, G, G, G, G, G, G, R, G, G, T,
                     G, G, G, R, R, T, G, G, G, G, G, G, R, R, G, G,
                     R, R, R, R, G, G, G, G, G, G, G, G, G, R, R, R,
                     G, G, G, G, G, G, G, G, G, G, G, G, G, T, R, R,
                     G, G, G, G, G, G, G, G, G, G, G, G, G, G, R, G,
                     R, R, R, R, G, G, G, G, T, G, G, G, R, R, R, G,
                     G, T, G, R, R, R, R, G, G, G, G, G, R, G, G, G,
                     G, G, G, G, G, G, R, R, R, R, R, R, R, G, T, G,
                     G, G, G, G, G, T, G, G, G, G, G, G, G, G, G, G,
                     G, G, G, G, G, G, G, G, G, G, T, G, G, G, G, G,)
    default_board_string = '|'.join(default_board)

    def __init__(self, game, move_no=0):
        self.board = None
        if move_no:
            self.board = Board.objects.filter(game=game, move_no=move_no)
            if not self.board:
                # raise
                pass
        else:
            self.board = Board(game=game,
                          move_no=1,
                          rows=self.rows,
                          columns=self.columns,
                          board=self.default_board_string)
        self._parse_state(self.board.board)


    def _parse_state(self, board_str):
        self.cells = board_str.split('|')
