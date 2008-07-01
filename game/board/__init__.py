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
                if '!' in cell_str:
                    return Ground(special=Catastrophe())
                elif '?' in cell_str:
                    civ_type = cell_str[2]
                    if civ_type == 's':
                        return Ground(piece=SettlementCiv(), special=Unification())
                    elif civ_type == 't':
                        return Ground(piece=TempleCiv(), special=Unification())
                    elif civ_type == 'm':
                        return Ground(piece=MerchantCiv(), special=Unification())
                else:
                    return Ground()
            elif cell_str.startswith('R'):
                if '!' in cell_str:
                    return River(special=Catastrophe())
                elif '?' in cell_str:
                    return River(piece=FarmCiv(), special=Unification()) 
                else:
                    return River()
            elif cell_str.startswith('s'):
                return Ground(piece=SettlementCiv())
            elif cell_str.startswith('t'):
                return Ground(piece=TempleCiv())
            elif cell_str.startswith('f'):
                return River(piece=FarmCiv())
            elif cell_str.startswith('m'):
                return Ground(piece=MerchantCiv())
            elif cell_str.startswith('T'):
                return Ground(piece=TempleCiv(is_treasure=True))
            elif cell_str.startswith('r'):
                ruler_type = cell_str[2]
                ruler_player_no = cell_str[1]
                if ruler_type == 's':
                    return Ground(piece=SettlementRuler(ruler_player_no))
                elif ruler_type == 't':
                    return Ground(piece=TempleRuler(ruler_player_no))
                elif ruler_type == 'f':
                    return River(piece=FarmRuler(ruler_player_no))
                elif ruler_type == 'm':
                    return Ground(piece=MerchantRuler(ruler_player_no))
            elif cell_str.startswith('M'):
                pass

        self.cells = [ convert(x) for x in board_str.split('|')]

    def save(self):
        self.board.save()
