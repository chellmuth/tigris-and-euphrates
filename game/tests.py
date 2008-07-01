import unittest
from game.models import Game
from game.board import StandardBoard

class StandardBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        
    def testBoardParsing(self):
        board = StandardBoard(self.game)
        board._parse_state('G|R|s|t|f|m|!|?|r1s|T')

        self.assertEquals([ str(x.__class__) for x in board.cells ], 
                          ['game.board.cell.Ground', 
                           'game.board.cell.River',
                           'game.board.piece.SettlementCiv',
                           'game.board.piece.TempleCiv',
                           'game.board.piece.FarmCiv',
                           'game.board.piece.MerchantCiv',
                           'game.board.special.Catastrophe',
                           'game.board.special.Unification',
                           'game.board.piece.SettlementRuler',
                           'game.board.piece.TempleCiv'])
        self.assertEquals(board._db_form(), 'G|R|s|t|f|m|!|?|r1s|T')
