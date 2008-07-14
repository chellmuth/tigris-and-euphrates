import unittest
from game.models import Game, CivBag, Player
from game.board import StandardBoard
from game.board.cell import Ground, River
from game.board import identify_regions, identify_kingdoms, adjacent_kingdoms_by_cell_no, legal_ruler_cells, pieces_by_region, adjacent_temples_by_cell_no, build_board_data, safe_tile, external_war_tile, safe_ruler, internal_war_ruler

class GameIntegrityTestCase(unittest.TestCase):
    def testGame(self):
        p1 = Player.objects.create(user_name = 'P1')
        p2 = Player.objects.create(user_name = 'P2')
        p3 = Player.objects.create(user_name = 'P3')
        p4 = Player.objects.create(user_name = 'P4')

        game = Game.objects.create(player_1=p1, player_2=p2, player_3=p3, player_4=p4, turn_no=0)
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
        res = identify_regions(board)
        self.assertEquals(res, [0, 0, 5, 5, 0, 4, 0, 0, 0, 3, 0, 0, 0, 0, 0, 2, 2, 0, 1, 0])

        res = identify_kingdoms(res, board)
        self.assertEquals(res, [0, 0, 5, 5, 0, -4, -0, -0, -0, -3, -0, -0, -0, -0, -0, -2, -2, -0, -1, -0])

#     def testLegalRulerMoves(self):
#         board = StandardBoard(self.game)
#         board.rows = 3
#         board.columns = 2
#         board._parse_state('t|G|r1t|G|t|G')

#         get_legal_ruler_moves(board)

    def test_adjacent_kingdoms_by_cell_no(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('t|G|G|G|t|r1t|G|s|G|G|G|r1s|s|s|G|s')

        res = identify_regions(board)
        res = identify_kingdoms(res, board)
        res = adjacent_kingdoms_by_cell_no(board, res)

        self.assertEquals(res,  [[],  [3], [],     [1], 
                                 [],  [],  [1, 3], [], 
                                 [3], [3], [1],    [], 
                                 [],  [],  [1],    []   ])

        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('r1s|s|r1t|s|G|t|G|G|r1f|G|r1m|s|s|s|G|s')

        res = identify_regions(board)
        res = identify_kingdoms(res, board)
        res = adjacent_kingdoms_by_cell_no(board, res)

        self.assertEquals(res,  [[],     [],        [],     [], 
                                 [2, 3], [],        [1, 3], [1, 3], 
                                 [],     [1, 2, 3], [],     [], 
                                 [],     [],        [1, 2], []      ])

        board = StandardBoard(self.game)
        board.rows = 5
        board.columns = 5
        board._parse_state('G|G|s|G|G|G|G|r1s|G|G|r2s|s|G|s|r3s|G|G|s|G|G|G|G|r4s|G|G')

        res = identify_regions(board)
        res = identify_kingdoms(res, board)
        res = adjacent_kingdoms_by_cell_no(board, res)

        self.assertEquals(res,  [[],  [4],    [],           [4],    [],
                                 [3], [3,4],  [],           [2, 4], [2],
                                 [],  [],     [1, 2, 3, 4], [],     [],
                                 [3], [1, 3], [],           [1, 2], [2], 
                                 [],  [1],    [],           [1],    []   ])

    def test_legal_ruler_cells(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('G|t|G|t|s|r1t|G|G|G|G|G|s|G|t|r2t|t')
        
        res = identify_regions(board)
        res = identify_kingdoms(res, board)

        res = legal_ruler_cells(board, res)

        self.assertEquals(res, [ 0, 2, 7, 12 ])


    def test_legal_ruler_cells__catastrophe_not_okay(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('G|t|G!|t|s|r1t|G|G|G|G|G|s|G|G!|r2t|t')
        
        res = identify_regions(board)
        res = identify_kingdoms(res, board)

        res = legal_ruler_cells(board, res)

        self.assertEquals(res, [ 0, 7 ])
        
    def test_legal_ruler_cells__river_not_okay(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('s|G|G|t|t|r1t|G|R|G|G|s|s|s|t|r2t|t')
        
        res = identify_regions(board)
        res = identify_kingdoms(res, board)

        res = legal_ruler_cells(board, res)

        self.assertEquals(res, [ 2 ])

    def test_legal_ruler_cells__treasure_okay(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('s|G|G|T|t|r1t|G|G|G|G|s|s|s|t|r2t|t')
        
        res = identify_regions(board)
        res = identify_kingdoms(res, board)

        res = legal_ruler_cells(board, res)

        self.assertEquals(res, [ 2, 7 ])

    def test_adjacent_temples_by_cell_no(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('s|G|G|T|t|r1t|G|G|G|G|s|s|s|t|r2t|t')

        res = adjacent_temples_by_cell_no(board)
        self.assertEquals(res, [[4], [], [3], [], [], [4], [], [3], [4], [13], [], [15], [13], [], [13, 15], []])

    def test_adjacent_temples_by_cell_no(self):
        board = StandardBoard(self.game)
        board.rows = 4
        board.columns = 4
        board._parse_state('s|G|G|T|t|r1t|G|G|G|G|s|s|s|t|r2t|t')

        build_board_data(board)

        safe = [ cell_no for cell_no, cell in enumerate(board) if safe_tile(board, cell_no, cell.is_ground) ]
        external_war = [ cell_no for cell_no, cell in enumerate(board) if external_war_tile(board, cell_no, cell.is_ground) ]

        safe_temples = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-temple') ]
        safe_settlements = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-settlement') ]
        safe_farms = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-farm') ]
        safe_merchants = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-merchant') ]
        
        war_temples = [ cell_no for cell_no, cell in enumerate(board) if internal_war_ruler(board, cell_no, 'ruler-temple') ]
        war_settlements = [ cell_no for cell_no, cell in enumerate(board) if internal_war_ruler(board, cell_no, 'ruler-settlement') ]
        war_farms = [ cell_no for cell_no, cell in enumerate(board) if internal_war_ruler(board, cell_no, 'ruler-farm') ]
        war_merchants = [ cell_no for cell_no, cell in enumerate(board) if internal_war_ruler(board, cell_no, 'ruler-merchant') ]


        self.assertEquals(safe, [1, 2, 7])
        self.assertEquals(external_war, [6, 8, 9])
        self.assertEquals(safe_temples, [2])
        self.assertEquals(safe_settlements, [1, 2, 7])
        self.assertEquals(safe_farms, [1, 2, 7])
        self.assertEquals(safe_merchants, [1, 2, 7])
        self.assertEquals(war_temples, [1, 7])
        self.assertEquals(war_settlements, [])

#     def test_build_board_data(self):
#         board = StandardBoard(self.game)
#         board.rows = 4
#         board.columns = 4
#         board._parse_state('s|G|G|t|t|r1t|G|G|G|G|m|r2f|s|t|r1s|t')
        
#         build_board_data(board)
#         assert(0)
# [{'farm': [], 'rulers': [], 'settlement': [], 'temple': [], 'merchant': []}, {'farm': [], 'rulers': [('ruler-farm', '2', 11), ('ruler-settlement', '1', 14)], 'settlement': [12], 'temple': [13, 15], 'merchant': [10]}, {'farm': [], 'rulers': [('ruler-temple', '1', 5)], 'settlement': [0], 'temple': [4], 'merchant': []}, {'farm': [], 'rulers': [], 'settlement': [], 'temple': [3], 'merchant': []}]
