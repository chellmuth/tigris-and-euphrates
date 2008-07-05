from django.shortcuts import render_to_response
from django.http import HttpResponse

from game.models import Game, CivBag
from game.board import StandardBoard
from game.board import split_legal_moves_by_type
from game.board.piece import SettlementCiv

import datetime

def current_datetime(request):
    current_date = datetime.datetime.now()
    return render_to_response('current_datetime.html', locals())

def hours_ahead(request, offset):
    hour_offset = int(offset)
    next_time = datetime.datetime.now() + datetime.timedelta(hours=hour_offset)
    return render_to_response('hours_ahead.html', locals())

def drop_civ(request,civ,cell):
    civ = int(civ)
    cell = int(cell)

    g = Game()
    board = StandardBoard(g)

    legal_moves = split_legal_moves_by_type(board)
    if cell in legal_moves['ground']:
        board[cell].piece = SettlementCiv()

    return HttpResponse('hi')

def print_custom_css_board(request, rows, cols, size):
    css_classes = []
    div_decls = []
    js_script = []

    g = Game()
    board = StandardBoard(g)

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
        if board[cell_no].has_piece():
            cell_class += ' ' + board[cell_no].css_class_name()
            
        div_decls.append('<div id="drop%s" class="%s"></div>' % (cell_no, cell_class))

        accept_class = ''
        if cell_no %8 == 0:
            accept_class = '.river'
        else:
            accept_class = '.ground'

    return render_to_response('board_test.html', locals())

def game_state_json(request):
    g = Game()
    board = StandardBoard(g)
    moves = split_legal_moves_by_type(board)

    bag = CivBag(g)
    tiles = [ bag.get_piece(),bag.get_piece(),bag.get_piece(),bag.get_piece(),bag.get_piece(),bag.get_piece() ]
    tiles = [ tile.unique_id() for tile in tiles]
    str = """
[
  { "legal_ground_moves": %s },
  { "legal_river_moves": %s },
  { "player_hand": %s }
]
""" % (moves['ground'], moves['river'], tiles)
    
    print str

    resp = HttpResponse(str)
    resp.headers['Content-Type'] = 'text/javascript'

    return resp
