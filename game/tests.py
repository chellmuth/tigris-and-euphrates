import unittest
from game.models import Game, CivBag, Player
from game.board import StandardBoard
from game.board.cell import Ground, River
from game.board import identify_groups, identify_kingdoms, get_legal_civ_moves

class GameIntegrityTestCase(unittest.TestCase):
    def testGame(self):
        p1 = Player.objects.create(user_name = 'P1')
        p2 = Player.objects.create(user_name = 'P2')
        p3 = Player.objects.create(user_name = 'P3')
        p4 = Player.objects.create(user_name = 'P4')

        game = Game.objects.create(player_1=p1, player_2=p2, player_3=p3, player_4=p4, turn=0)
        board = StandardBoard(game)
        bag = CivBag(game)
        

class CivBagTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game.objects.create()

    def testBag(self):
        bag = CivBag(self.game)
        self.assertEquals([ bag.temple_start, bag.temple_remaining,
                            bag.farm_start, bag.farm_remaining,
                            bag.merchant_start, bag.merchant_remaining,
                            bag.settlement_start, bag.settlement_remaining ],
                          [ 57, 57,
                            36, 36,
                            30, 30,
                            30, 30 ])

        list = []
        for i in range(57 + 36 + 30 + 30):
            list.append(bag.get_piece())

        for i in range(57):
            if not [ 1 for civ_piece in list if civ_piece.unique_id() == ('t' + str(i)) ]:
                self.assertEquals(0,1)
        for i in range(36):
            if not [ 1 for civ_piece in list if civ_piece.unique_id() == ('f' + str(i)) ]:
                self.assertEquals(0,1)
        for i in range(30):
            if not [ 1 for civ_piece in list if civ_piece.unique_id() == ('m' + str(i)) ]:
                self.assertEquals(0,1)
        for i in range(30):
            if not [ 1 for civ_piece in list if civ_piece.unique_id() == ('s' + str(i)) ]:
                self.assertEquals(0,1)

        print [ piece.unique_id() for piece in list]
                
class StandardBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        
    def testBoardParsing(self):
        board = StandardBoard(self.game)
        board._parse_state('G|R|s|t|f|m|G!|R!|G?m|R?|r1s|T')

        self.assertEquals([ (x.piece and str(x.piece.__class__),
                             x.special and str(x.special.__class__),
                             str(x.__class__),) 
                            for x in board.cells], 

                          [(None,                               None,                             'game.board.cell.Ground'), 
                           (None,                               None,                             'game.board.cell.River' ),
                           ('game.board.piece.SettlementCiv',   None,                             'game.board.cell.Ground'),
                           ('game.board.piece.TempleCiv',       None,                             'game.board.cell.Ground'),
                           ('game.board.piece.FarmCiv',         None,                             'game.board.cell.River' ),
                           ('game.board.piece.MerchantCiv',     None,                             'game.board.cell.Ground'),
                           (None,                               'game.board.special.Catastrophe', 'game.board.cell.Ground'),
                           (None,                               'game.board.special.Catastrophe', 'game.board.cell.River' ),
                           ('game.board.piece.MerchantCiv',     'game.board.special.Unification', 'game.board.cell.Ground'),
                           ('game.board.piece.FarmCiv',         'game.board.special.Unification', 'game.board.cell.River' ),
                           ('game.board.piece.SettlementRuler', None,                             'game.board.cell.Ground'),
                           ('game.board.piece.TempleCiv',       None,                             'game.board.cell.Ground'),
                           ])

        self.assertEquals(board._db_form(), 'G|R|s|t|f|m|G!|R!|G?m|R?|r1s|T')

    def testBoardListBehavior(self):
        board = StandardBoard(self.game)
        board._parse_state('G|R|T')

        self.assertEquals(str(board[0].__class__), 'game.board.cell.Ground')
        self.assertEquals(str(board[1].__class__), 'game.board.cell.River')
        self.assertEquals(str(board[-1].__class__), 'game.board.cell.Ground')

        for cell, dummy_cell in zip(board, [Ground(), River(), Ground()]):
            self.assertEquals(cell.__class__, dummy_cell.__class__)
                            

        board[0] = River()
        self.assertEquals(str(board[0].__class__), 'game.board.cell.River')

        self.assertEquals(len(board), 3)


    def testIdentifyGroups(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 5
        board._parse_state('G|R|s|r1t|R|t|G|G|G|t|R|R|R|R|R|t|t|G|t|G')
        res = identify_groups(board)
        self.assertEquals(res, [0, 0, 5, 5, 0, 4, 0, 0, 0, 3, 0, 0, 0, 0, 0, 2, 2, 0, 1, 0])

        res = identify_kingdoms(res, board)
        self.assertEquals(res, [0, 0, 5, 5, 0, -4, -0, -0, -0, -3, -0, -0, -0, -0, -0, -2, -2, -0, -1, -0])
