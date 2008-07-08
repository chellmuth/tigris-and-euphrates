from django.shortcuts import render_to_response
from django.http import HttpResponse

from game.models import Game, CivBag, Hand, Player
from game.board import StandardBoard
from game.board import split_legal_moves_by_type
from game.board.piece import SettlementCiv, FarmCiv, TempleCiv, MerchantCiv

def _convert(str):
    if str[0] == 's':
        return SettlementCiv()
    if str[0] == 'm':
        return MerchantCiv()
    if str[0] == 'f':
        return FarmCiv()
    if str[0] == 't':
        return TempleCiv()
    
def drop_civ(request, civ, cell):
    civ = int(civ)
    cell = int(cell)

    g = Game.objects.get(id=1)
    board = StandardBoard(g,1)
    p = Player.objects.filter(user_name='cjh').get()
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    
    legal_moves = split_legal_moves_by_type(board)
    if cell in legal_moves['ground']:
        board.add_civ(cell, _convert(hand.__getattribute__('piece' + str(civ))))
        hand.swap(civ)
        
    board.save()
    hand.save()

    return game_state_json(request)

def print_custom_css_board(request, rows, cols, size):
    css_classes = []
    div_decls = []
    js_script = []

    g = Game.objects.get(id=1)
    board = StandardBoard(g,1)

    for cell_no in range(rows * cols):
        row = cell_no / cols
        col = cell_no % cols

        css_string = """#drop%s {
width: %spx;
height: %spx;
position: absolute;
top: %spx;
left: %spx;
}
""" % (cell_no, size, size, row * size, col * size)
        css_classes.append(css_string)

        cell_class = board[cell_no].is_ground and 'cell-ground' or 'cell-river'
            
        div_decls.append('<div id="drop%s" class="%s"></div>' % (cell_no, cell_class))

    return render_to_response('board_test.html', locals())

def game_state_json(request):
    g = Game.objects.get(id=1)
    board = StandardBoard(g,1)
    moves = split_legal_moves_by_type(board)

    p = Player.objects.filter(user_name='cjh').get()
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    
    tiles = [ hand.piece0, hand.piece1, hand.piece2, hand.piece3, hand.piece4, hand.piece5 ]
    str = """
[
  { "legal_ground_moves": %s },
  { "legal_river_moves": %s },
  { "player_hand": %s },
  { "temple_civ": %s },
  { "settlement_civ": %s },
  { "farm_civ": %s },
  { "merchant_civ": %s }
]
""" % (moves['ground'], moves['river'], tiles, board.get_cell_no_for_civ('t'), board.get_cell_no_for_civ('s'), board.get_cell_no_for_civ('f'), board.get_cell_no_for_civ('m'))
    
    print str

    resp = HttpResponse(str)
    resp.headers['Content-Type'] = 'text/javascript'

    return resp

def create_board(request):
    css_classes = []
    div_decls = []

    g = Game.objects.create()
    board = StandardBoard(g)

    rows = board.rows
    cols = board.columns
    size = 50

    moves = split_legal_moves_by_type(board)
    config_drop_str = """
$.each(%s, function(i, item) { config_drop(item, 'ground'); });
$.each(%s, function(i, item) { config_drop(item, 'river'); });
""" % (moves['ground'], moves['river'])
    
    for cell_no in range(rows * cols):
        row = cell_no / cols
        col = cell_no % cols

        css_string = """#drop%s {
width: %spx;
height: %spx;
position: absolute;
top: %spx;
left: %spx;
}
""" % (cell_no, size, size, row * size, col * size)
        css_classes.append(css_string)

        cell_class = board[cell_no].is_ground and 'cell-ground' or 'cell-river'
            
        div_decls.append('<div id="drop%s" class="%s"></div>' % (cell_no, cell_class))

    return render_to_response('create_situation.html', locals())
