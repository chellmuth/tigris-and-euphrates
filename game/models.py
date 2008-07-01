from django.db import models

class Game(models.Model):
    pass

class Board(models.Model):
    game = models.ForeignKey(Game)
    move_no = models.IntegerField()
    rows = models.IntegerField()
    columns = models.IntegerField()
    board = models.TextField()
