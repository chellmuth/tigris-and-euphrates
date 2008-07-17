from django.shortcuts import render_to_response
from django.http import HttpResponse

from game.models import Game, CivBag, Hand, Player
from game.board import StandardBoard, build_board_data
from game.board import split_legal_moves_by_type, safe_tile, safe_ruler
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
    

def create_game(request):
    p1 = Player.objects.create(user_name='cjh')
    p2 = Player.objects.create(user_name='test')
    
    game = Game.objects.create(player_1=p1, player_2=p2)

    bag = CivBag.objects.create(game=game)
    p1_hand = Hand.objects.create(game=game, player=p1, turn_no=game.turn_no, action_no=game.action_no,
                                  piece0=bag.get_piece().unique_id(), piece1=bag.get_piece().unique_id(),
                                  piece2=bag.get_piece().unique_id(), piece3=bag.get_piece().unique_id(),
                                  piece4=bag.get_piece().unique_id(), piece5=bag.get_piece().unique_id())
    p2_hand = Hand.objects.create(game=game, player=p2, turn_no=game.turn_no, action_no=game.action_no,
                                  piece0=bag.get_piece().unique_id(), piece1=bag.get_piece().unique_id(),
                                  piece2=bag.get_piece().unique_id(), piece3=bag.get_piece().unique_id(),
                                  piece4=bag.get_piece().unique_id(), piece5=bag.get_piece().unique_id())

    board = StandardBoard(game=game)

    p1.save()
    p2.save()
    game.save()
    bag.save()
    p1_hand.save()
    p2_hand.save()
    board.save()

    return HttpResponse()

def drop_ruler(request, player_no, ruler, cell):
    cell = int(cell)

    g = Game.objects.get(id=1)
    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)

    moves = [ cell_no for cell_no, cell_obj in enumerate(board) if safe_ruler(board, cell_no, ruler, player_no) ]

    if cell in moves:
        board.add_ruler(cell, ruler, player_no)
        
    board.save()

    return game_state_json(request, player_no)

def drop_civ(request, player_no, civ, cell):
    civ = int(civ)
    cell = int(cell)

    g = Game.objects.get(id=1)
    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    
    moves = []
    civ_obj = _convert(hand.__getattribute__('piece' + str(civ)))

    if civ_obj.name() == 'civ-farm':
        moves = [ cell_no for cell_no, cell_obj in enumerate(board) if safe_tile(board, cell_no, is_ground=False) ]
    else:
        moves = [ cell_no for cell_no, cell_obj in enumerate(board) if safe_tile(board, cell_no, is_ground=True) ]

    if cell in moves:
        board.add_civ(cell, _convert(hand.__getattribute__('piece' + str(civ))))
        hand.swap(civ)
        
    board.save()
    hand.save()

    return game_state_json(request, player_no)

def print_custom_css_board(request, player_no, rows, cols, size):
    css_classes = []
    div_decls = []
    js_script = []
    player_no = int(player_no)

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

    board_css = """#board {
width: %spx;
height: %spx;
position:absolute;
top: %spx;
left: %spx;
}
""" % (cols*size, rows*size, 0, 0)

    ruler_prefix = player_no == 1 and 'A' or 'B'

    return render_to_response('board_test.html', locals())

def game_state_json(request, player_no):
    g = Game.objects.get(id=1)
    board = StandardBoard(g,1)
    build_board_data(board)

    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    
    ground_moves = [ cell_no for cell_no, cell in enumerate(board) if safe_tile(board, cell_no, is_ground=True) ]
    river_moves = [ cell_no for cell_no, cell in enumerate(board) if safe_tile(board, cell_no, is_ground=False) ]

    safe_temples = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-temple', player_no) ]
    safe_settlements = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-settlement', player_no) ]
    safe_farms = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-farm', player_no) ]
    safe_merchants = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-merchant', player_no) ]

    tiles = [ hand.piece0, hand.piece1, hand.piece2, hand.piece3, hand.piece4, hand.piece5 ]
    str = """
{
   "legal_ground_moves": %s,
   "legal_river_moves": %s,
   "legal_ruler_moves": 
       { "temple": %s,
         "settlement": %s,
         "farm": %s,
         "merchant": %s
       },
   "player_hand": %s,
   "temple_civ": %s,
   "settlement_civ": %s,
   "farm_civ": %s, 
   "merchant_civ": %s,
   "temple_ruler": %s,
   "settlement_ruler": %s,
   "farm_ruler": %s, 
   "merchant_ruler": %s
}
""" % (ground_moves, river_moves, safe_temples, safe_settlements, safe_farms, safe_merchants, tiles, board.get_cell_no_for_civ('t') + board.get_cell_no_for_civ('T'), board.get_cell_no_for_civ('s'), board.get_cell_no_for_civ('f'), board.get_cell_no_for_civ('m'), board.get_cell_and_player_nos_for_ruler('t'), board.get_cell_and_player_nos_for_ruler('s'), board.get_cell_and_player_nos_for_ruler('f'), board.get_cell_and_player_nos_for_ruler('m'))
    
#    print str

    resp = HttpResponse(str)
    resp.headers['Content-Type'] = 'text/javascript'

    return resp
