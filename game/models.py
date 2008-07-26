from django.db import models
from game.board.piece import SettlementCiv, FarmCiv, MerchantCiv, TempleCiv

import random

class Player(models.Model):
    user_name = models.CharField(maxlength=100)

class Game(models.Model):
    player_1 = models.ForeignKey(Player, related_name='player_1_player', blank=True, null=True)
    player_2 = models.ForeignKey(Player, related_name='player_2_player', blank=True, null=True)
    player_3 = models.ForeignKey(Player, related_name='player_3_player', blank=True, null=True)
    player_4 = models.ForeignKey(Player, related_name='player_4_player', blank=True, null=True)

    turn_no = models.IntegerField(default=0)
    action_no = models.IntegerField(default=0)
    
    player_1_points_farm = models.IntegerField(default=0)
    player_1_points_settlement = models.IntegerField(default=0)
    player_1_points_temple = models.IntegerField(default=0)    
    player_1_points_farm = models.IntegerField(default=0)
    player_1_points_treasure = models.IntegerField(default=0)

    player_2_points_farm = models.IntegerField(default=0)
    player_2_points_settlement = models.IntegerField(default=0)
    player_2_points_temple = models.IntegerField(default=0)    
    player_2_points_farm = models.IntegerField(default=0)
    player_2_points_treasure = models.IntegerField(default=0)

class Hand(models.Model):
    player = models.ForeignKey(Player)
    turn_no = models.IntegerField()
    action_no = models.IntegerField()
    game = models.ForeignKey(Game)

    piece0 = models.CharField(maxlength=3)
    piece1 = models.CharField(maxlength=3)
    piece2 = models.CharField(maxlength=3)
    piece3 = models.CharField(maxlength=3)
    piece4 = models.CharField(maxlength=3)
    piece5 = models.CharField(maxlength=3)

    def swap(self, piece_no):
        bag = CivBag.objects.filter(game=self.game).get()
        new_piece = bag.get_piece()
        self.__setattr__('piece' + str(piece_no), new_piece.unique_id())
        bag.save()

    def remove(self, piece_no):
        self.__setattr__('piece' + str(piece_no), 'XXX')
        
class Board(models.Model):
    game = models.ForeignKey(Game)
    turn_no = models.IntegerField(default=0)
    action_no = models.IntegerField(default=0)
    rows = models.IntegerField()
    columns = models.IntegerField()
    board = models.TextField()

class CivBag(models.Model):
    game = models.ForeignKey(Game)

    temple_start = models.IntegerField(default=57)
    temple_remaining = models.IntegerField(default=57)

    farm_start = models.IntegerField(default=36)
    farm_remaining = models.IntegerField(default=36)

    merchant_start = models.IntegerField(default=30)
    merchant_remaining = models.IntegerField(default=30)

    settlement_start = models.IntegerField(default=30)
    settlement_remaining = models.IntegerField(default=30)

    def get_piece(self):
        ran = random.randint(0, sum([self.settlement_remaining, self.farm_remaining, self.merchant_remaining, self.temple_remaining]) - 1)
        
        civ_sum = 0
        if 0 <= ran < civ_sum + self.settlement_remaining:
            self.settlement_remaining -= 1
            return SettlementCiv(self.settlement_start - self.settlement_remaining - 1) # preseve 0-indexing on ids

        civ_sum += self.settlement_remaining
        if civ_sum <= ran < civ_sum + self.farm_remaining:
            self.farm_remaining -= 1
            return FarmCiv(self.farm_start - self.farm_remaining - 1)

        civ_sum += self.farm_remaining
        if civ_sum <= ran < civ_sum + self.merchant_remaining:
            self.merchant_remaining -= 1
            return MerchantCiv(self.merchant_start - self.merchant_remaining - 1)

        civ_sum += self.merchant_remaining
        if civ_sum <= ran < civ_sum + self.temple_remaining:
            self.temple_remaining -= 1
            return TempleCiv(self.temple_start - self.temple_remaining - 1)

        assert(0)
