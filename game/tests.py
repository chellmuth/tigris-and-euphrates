import unittest
from game.models import Game
from game.board import StandardBoard

class StandardBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        
    def testBoardParsing(self):
        board = StandardBoard(self.game)
        board._parse_state('G|R|s|t|f|m|G!|R!|G?m|R?|r1s|T')

        self.assertEquals([ (x.piece and str(x.piece.__class__),
                             x.special and str(x.special.__class__),
                             str(x.__class__),) for x in board.cells ], 
                          [(None, None, 'game.board.cell.Ground'), 
                           (None, None, 'game.board.cell.River'),
                           ('game.board.piece.SettlementCiv', None, 'game.board.cell.Ground'),
                           ('game.board.piece.TempleCiv', None, 'game.board.cell.Ground'),
                           ('game.board.piece.FarmCiv', None, 'game.board.cell.River'),
                           ('game.board.piece.MerchantCiv', None, 'game.board.cell.Ground'),
                           (None, 'game.board.special.Catastrophe', 'game.board.cell.Ground'),
                           (None, 'game.board.special.Catastrophe', 'game.board.cell.River'),
                           ('game.board.piece.MerchantCiv', 'game.board.special.Unification', 'game.board.cell.Ground'),
                           ('game.board.piece.FarmCiv', 'game.board.special.Unification', 'game.board.cell.River'),
                           ('game.board.piece.SettlementRuler', None, 'game.board.cell.Ground'),
                           ('game.board.piece.TempleCiv', None, 'game.board.cell.Ground'),])

        self.assertEquals(board._db_form(), 'G|R|s|t|f|m|G!|R!|G?m|R?|r1s|T')
