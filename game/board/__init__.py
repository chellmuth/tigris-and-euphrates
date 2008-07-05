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

    def __iter__(self):
        return self.cells.__iter__()

    def __len__(self):
        return self.cells.__len__()

    def __getitem__(self, x):
        return self.cells.__getitem__(x)

    def __setitem__(self, x, y):
        return self.cells.__setitem__(x, y)

def identify_groups(board):
    """Give a board
    Return an array where array[cell_no] is cell's group_no
    Where group_no = 0 means uncolonized
    """
    main_stack = [(cell, cell_no) for cell, cell_no in zip(board, range(len(board)))]
    cell_no_visited = [ 0 for x in main_stack ]
    
    for cell, cell_no in main_stack:
        cell_no_visited[cell_no] = 0
    
    def _label_all_neighbors(cell_no, group_count):
        if cell_no_visited[cell_no]:
            return
     
        cur_row = cell_no / board.columns
        cur_col = cell_no % board.columns
     
        cell_no_visited[cell_no] = group_count
     
        top_index = cell_no - board.columns
        if cur_row - 1 >= 0 and board[top_index].has_piece() and not cell_no_visited[top_index]:
            _label_all_neighbors(top_index, group_count)

        bottom_index = cell_no + board.columns
        if cur_row + 1 < board.rows and board[bottom_index].has_piece() and not cell_no_visited[bottom_index]:
            _label_all_neighbors(bottom_index, group_count)

        left_index = cell_no - 1
        if cur_col - 1 >= 0 and board[left_index].has_piece() and not cell_no_visited[left_index]:                         
            _label_all_neighbors(left_index, group_count)

        right_index = cell_no + 1
        if cur_col + 1 < board.columns and board[right_index].has_piece() and not cell_no_visited[right_index]:
            _label_all_neighbors(right_index, group_count)

    group_count = 1
    while main_stack:
        cell, cell_no = main_stack.pop()
        if not cell_no_visited[cell_no] and cell.has_piece():
            _label_all_neighbors(cell_no, group_count)
            group_count+=1

    return cell_no_visited

def identify_kingdoms(group_list, board):
    assert(len(group_list) == len(board))
    
    groups = set()
    for group_no, cell in zip(group_list, board):
        if cell.has_ruler():
            groups.add(group_no)

    return [ (lambda x: x in groups and x or -x)(x) for x in group_list ]


def get_legal_moves(board):
    return get_legal_civ_moves(board)

def get_legal_civ_moves(board):
    legal_spots = []
    kingdoms = identify_kingdoms(identify_groups(board), board)
    assert(len(kingdoms) == len(board))
    
    for cell, kingdom_id, cell_no in zip(board, kingdoms, range(len(board))):
        if kingdom_id == 0:
            adjacent_kindoms = set()

            cur_row = cell_no / board.columns
            cur_col = cell_no % board.columns
            
            top_index = cell_no - board.columns
            if cur_row - 1 >= 0 and kingdoms[top_index] > 0:
                adjacent_kindoms.add(kingdoms[kingdom_id])
     
            bottom_index = cell_no + board.columns
            if cur_row + 1 < board.rows and kingdoms[bottom_index] > 0:
                adjacent_kindoms.add(kingdoms[kingdom_id])
     
            left_index = cell_no - 1
            if cur_col - 1 >= 0 and kingdoms[left_index] > 0:
                adjacent_kindoms.add(kingdoms[kingdom_id])
     
            right_index = cell_no + 1
            if cur_col + 1 < board.columns and kingdoms[right_index] > 0:
                adjacent_kindoms.add(kingdoms[kingdom_id])
            
            adjacent_kindoms.discard(kingdom_id)
            if len(adjacent_kindoms) < 2:
                legal_spots.append(cell_no)
    return legal_spots

def split_legal_moves_by_type(board):
    legal_moves = get_legal_civ_moves(board)
    legal_ground = []
    legal_river = []

    for cell_no in legal_moves:
        if board[cell_no].is_ground:
            legal_ground.append(cell_no)
        else:
            legal_river.append(cell_no)

    return { 'ground': legal_ground,
             'river': legal_river }
