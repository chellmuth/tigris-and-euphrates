from game.models import Board
from game.board.cell import Ground, River
from game.board.piece import SettlementCiv, FarmCiv, TempleCiv, MerchantCiv, SettlementRuler, FarmRuler, TempleRuler, MerchantRuler, GroundMonument, RiverMonument
from game.board.special import Unification, Catastrophe

class StandardBoard:
    rows = 11
    columns = 16
    cells = []

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

    def _db_form(self):
        return '|'.join([ cell.db_form() for cell in self.cells])

    def _parse_state(self, board_str):
        def convert(cell_str):
            if cell_str.startswith('G'):
                return Ground()
            elif cell_str.startswith('R'):
                return River()
            elif cell_str.startswith('s'):
                return SettlementCiv() 
            elif cell_str.startswith('t'):
                return TempleCiv()
            elif cell_str.startswith('f'):
                return FarmCiv()
            elif cell_str.startswith('m'):
                return MerchantCiv()
            elif cell_str.startswith('!'):
                return Catastrophe()
            elif cell_str.startswith('?'):
                return Unification()
            elif cell_str.startswith('T'):
                return TempleCiv(is_treasure=True)
            elif cell_str.startswith('r'):
                ruler_type = cell_str[2]
                ruler_player_no = cell_str[1]
                if ruler_type == 's':
                    return SettlementRuler(ruler_player_no)
                elif ruler_type == 't':
                    return TempleRuler(ruler_player_no)
                elif ruler_type == 'f':
                    return FarmRuler(ruler_player_no)
                elif ruler_type == 'm':
                    return MerchantRuler(ruler_player_no)
            elif cell_str.startswith('M'):
                pass

        self.cells = [ convert(x) for x in board_str.split('|')]
