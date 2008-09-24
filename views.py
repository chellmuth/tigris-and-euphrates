from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from game.models import Game, CivBag, Hand, Player
from game.board import StandardBoard, build_board_data
from game.board import split_legal_moves_by_type, safe_tile, safe_ruler, external_war_tile, internal_war_ruler
from game.board.piece import SettlementCiv, FarmCiv, TempleCiv, MerchantCiv, SettlementRuler, FarmRuler, TempleRuler, MerchantRuler
from game.board.cell import Ground
from tigris.forms import GameCreateForm

def _convert(str):
    if str[0] == 's':
        return SettlementCiv()
    if str[0] == 'm':
        return MerchantCiv()
    if str[0] == 'f':
        return FarmCiv()
    if str[0] == 't':
        return TempleCiv()

def _convert_ruler(str, player_no):
    if str[0] == 's':
        return SettlementRuler(player_no)
    if str[0] == 'm':
        return MerchantRuler(player_no)
    if str[0] == 'f':
        return FarmRuler(player_no)
    if str[0] == 't':
        return TempleRuler(player_no)
    
def choose_treasure(request, game_id, player_no, cell_nos):
    cell_nos = [ int(x) for x in cell_nos.split("_") ]

    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)

    for cell_no in cell_nos:
        board[cell_no].piece.treasure = None

    attr_name = 'player_' + player_no + '_points_treasure'
    g.__setattr__(attr_name, g.__getattribute__(attr_name) + len(cell_nos))

    g.state = 'REGULAR'
    g.increment_action()
    g.save()

    board.save()

    return game_state_json(request, game_id, player_no)

def internal_defend(request, game_id, player_no, num_committed):
    num_committed = int(num_committed)

    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)

    defend_info = _get_defend_internal_info(g, board)

    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    if not hand.batch_remove('temple', num_committed): return False
    hand.save()

    defend_amount = num_committed + defend_info['defend_board']
    attack_amount = defend_info['attack_board'] + int(defend_info['attack_committed'])

    if defend_amount < attack_amount:
        board[defend_info['defend_cell_no']] = Ground()
        board[defend_info['attack_cell_no']].piece = _convert_ruler(defend_info['ruler_type'], defend_info['attack_player'])
    else:
        pass

    g.state = 'REGULAR'

    g.increment_action()

    g.save()
    board.save()
    
    return game_state_json(request, game_id, player_no)

def internal_attack(request, game_id, player_no, cell_no, civ, num_committed):
    cell_no = int(cell_no)

    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)
    
    if not internal_war_ruler(board, cell_no, 'ruler-' + civ, player_no): return False
    if not g.current_turn == int(player_no): return False

    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    if not hand.batch_remove('temple', num_committed): return False
    hand.save()

    g.state = 'INTERNAL|' + civ + "|" + str(cell_no) + "|" + num_committed

    g.waiting_for = _get_internal_defender(g, board, cell_no, civ)
    g.current_turn = player_no

    g.save()
    board.save()

    return game_state_json(request, game_id, player_no)
    
def defend_commit(request, game_id, player_no, tile_count):
    g = Game.objects.get(id=int(game_id))
    if not g.state.startswith('DEFEND'): return False

    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()

    civ = g.state.split("|")[1]

    if not int(player_no) == g.waiting_for: return False
    if not hand.batch_remove(civ, tile_count): return False

    hand.save()

    defend_info = _get_defend_info(g, board)

    losing_kindom = None
    if len(defend_info['attack_board']) + int(defend_info['attack_committed']) > len(defend_info['defend_board']) + int(tile_count):
        losing_kingdom = _get_defender_kingdom(g, board)

    else:
        losing_kingdom = _get_attacker_kingdom(g, board)

    board.external_war_removal(losing_kingdom, civ)

    build_board_data(board)

    unification_cell_no = board.find_unification_tile()
    more_war = external_war_tile(board, unification_cell_no)
    if more_war:
        g.state = 'CHOOSE_COLOR'
        g.waiting_for = g.current_turn
    else:
        g.state = "REGULAR"
        board[unification_cell_no].piece = _convert(board[unification_cell_no].special.piece)
        board[unification_cell_no].special = None

    g.increment_action()

    g.save()
    board.save()

    return game_state_json(request, game_id, player_no)

def attack_commit(request, game_id, player_no, tile_count):
    g = Game.objects.get(id=int(game_id))
    if not g.state.startswith('ATTACK'): return False

    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()

    civ = g.state.split("|")[1]

    if not int(player_no) == g.waiting_for: return False
    if not hand.batch_remove(civ, tile_count): return False
    hand.save()
    
    g.state = 'DEFEND|' + civ + "|" + tile_count

    g.waiting_for = _get_defender(g, board)
    g.save()

    return game_state_json(request, game_id, player_no)

def choose_color(request, game_id, player_no, civ):
    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)

    if not int(player_no) == g.waiting_for: return False

    g.state = 'ATTACK|' + civ
    g.waiting_for = _get_attacker(g, board)

    g.save()
    
    return game_state_json(request, game_id, player_no)

def external_war(request, game_id, player_no, civ, cell):
    civ = int(civ)
    cell = int(cell)

    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    
    moves = []
    civ_obj = _convert(hand.__getattribute__('piece' + str(civ)))

    if civ_obj.name() == 'civ-farm':
        moves = [ cell_no for cell_no, cell_obj in enumerate(board) if external_war_tile(board, cell_no, is_ground=False) ]
    else:
        moves = [ cell_no for cell_no, cell_obj in enumerate(board) if external_war_tile(board, cell_no, is_ground=True) ]

    if cell in moves and int(player_no) == g.current_turn:
        board.place_unification(cell, _convert(hand.__getattribute__('piece' + str(civ))))
        hand.remove(civ)
        g.state = 'CHOOSE_COLOR'
        g.waiting_for = player_no
    else: return False

    g.current_turn = player_no
    g.save()

    board.save()
    hand.save()

    return game_state_json(request, game_id,player_no)

def create_game(request):
    if request.method == 'POST':
        form = GameCreateForm(request.POST)
        if form.is_valid():
            _setup_game(name=form.clean_data['name'])
            return HttpResponseRedirect('/show_games/')
    else:
        form = GameCreateForm()

    return render_to_response('create_game.html', {
        'form': form,
    })

def _setup_game(name):
    p1 = Player.objects.create(user_name='cjh')
    p2 = Player.objects.create(user_name='test')
    
    game = Game.objects.create(player_1=p1, player_2=p2, name=name)

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

    p1_hand.turn_no, p2_hand.turn_no = 1, 1

    p1.save()
    p2.save()
    game.save()
    bag.save()
    p1_hand.save()
    p2_hand.save()
    board.save()

    return HttpResponse()

def drop_ruler(request, game_id, player_no, ruler, cell):
    cell = int(cell)

    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)
    p = g.__getattribute__('player_' + player_no)

    moves = [ cell_no for cell_no, _ in enumerate(board) if safe_ruler(board, cell_no, 'ruler-' + ruler, player_no) ]
    
    if cell in moves and int(player_no) == g.current_turn:
        board.add_ruler(cell, ruler, player_no)
    else: return False

    g.increment_action()

    g.save()
    board.save()

    return game_state_json(request, game_id, player_no)

def drop_civ(request, game_id, player_no, civ, cell):
    civ = int(civ)
    cell = int(cell)

    g = Game.objects.get(id=int(game_id))
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

    if cell in moves and int(player_no) == g.current_turn:
        point_to = board.get_point(cell, _convert(hand.__getattribute__('piece' + str(civ))))
        if point_to:
            attr_name = 'player_' + point_to + '_points_' + civ_obj.css_class_name()
            g.__setattr__(attr_name, g.__getattribute__(attr_name) + 1)
            
        board.add_civ(cell, _convert(hand.__getattribute__('piece' + str(civ))))
        build_board_data(board)
        hand.swap(civ)
        hand.save()
    else: return False

    treasure = board.treasure_to_claim()
    if treasure:
        g.waiting_for = treasure['player_no']
        g.state = 'TREASURE'
    else:
        g.increment_action()

    g.save()
    board.save()

    return game_state_json(request, game_id,player_no)

def print_custom_css_board(request, game_id, player_no, rows, cols, size):
    css_classes = []
    div_decls = []
    js_script = []
    player_no = int(player_no)
    board_start_x = 180
    board_start_y = 80

    g = Game.objects.get(id=int(game_id))
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
""" % (cell_no, size - 1, size - 1, row * size, col * size)
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

def _get_reposition_info(board, player_no, ruler_type):
    safe, war = [], []
    ruler_cell = board.is_ruler_placed('ruler-' + ruler_type, player_no)

    if ruler_cell:
        piece = board[ruler_cell].piece
        board[ruler_cell].piece = None
        build_board_data(board)

        safe = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-' + ruler_type, player_no) ]
        war = _get_internal_war_info(board, player_no, ruler_type)

        board[ruler_cell].piece = piece
        build_board_data(board)

    return safe, war

def game_state_json(request, game_id, player_no):
    g = Game.objects.get(id=int(game_id))
    board = StandardBoard(g,1)
    build_board_data(board)

    p = g.__getattribute__('player_' + player_no)
    hand = Hand.objects.filter(player=p, turn_no=1, game=g).get()
    
    ground_moves = [ cell_no for cell_no, cell in enumerate(board) if safe_tile(board, cell_no, is_ground=True) ]
    war_ground_moves = [ cell_no for cell_no, cell in enumerate(board) if external_war_tile(board, cell_no, is_ground=True) ]

    river_moves = [ cell_no for cell_no, cell in enumerate(board) if safe_tile(board, cell_no, is_ground=False) ]

    safe_temples = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-temple', player_no) ]
    safe_settlements = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-settlement', player_no) ]
    safe_farms = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-farm', player_no) ]
    safe_merchants = [ cell_no for cell_no, cell in enumerate(board) if safe_ruler(board, cell_no, 'ruler-merchant', player_no) ]

    safe_reposition_merchants, war_reposition_merchants = _get_reposition_info(board, player_no, 'merchant')
    safe_reposition_temples, war_reposition_temples = _get_reposition_info(board, player_no, 'temple')
    safe_reposition_settlements, war_reposition_settlements = _get_reposition_info(board, player_no, 'settlement')
    safe_reposition_farms, war_reposition_farms = _get_reposition_info(board, player_no, 'farm')

    war_temples = _get_internal_war_info(board, player_no, 'temple')
    war_settlements = _get_internal_war_info(board, player_no, 'settlement')
    war_farms = _get_internal_war_info(board, player_no, 'farm')
    war_merchants = _get_internal_war_info(board, player_no, 'merchant')

    tiles = [ hand.piece0, hand.piece1, hand.piece2, hand.piece3, hand.piece4, hand.piece5 ]

    player_no_prefix = "player_" + player_no + "_points_" 
    points = {}
    for civ in [ 'temple', 'settlement', 'farm', 'merchant', 'treasure' ]:
        points[civ] = g.__getattribute__(player_no_prefix + civ)

    attack_info = _get_attack_info(g, board)
    defend_info = _get_defend_info(g, board)

    defend_internal_info = _get_defend_internal_info(g, board)

    treasure_info = board.treasure_to_claim()
    if not treasure_info or player_no != treasure_info['player_no']:
        treasure_info['must_choose'] = []
        treasure_info['can_choose'] = []
        treasure_info['num_choose'] = 0

    state = (g.waiting_for == int(player_no)) and g.state or 'NOTYOU'

    json_str = """
{
   "legal_ground_moves": %s,
   "war_ground_moves": %s,
   "legal_river_moves": %s,
   "legal_ruler_moves": 
       { "temple": %s,
         "settlement": %s,
         "farm": %s,
         "merchant": %s
       },
   "legal_ruler_repositions":
       { "temple": %s,
         "settlement": %s,
         "farm": %s,
         "merchant": %s
       },
   "war_ruler_moves": 
       { "temple": %s,
         "settlement": %s,
         "farm": %s,
         "merchant": %s
       },
   "war_ruler_repositions":
       { "temple": %s,
         "settlement": %s,
         "farm": %s,
         "merchant": %s
       },
   "temple_count": %s, 
   "player_hand": %s,
   "unification": %s,
   "temple_civ": %s,
   "settlement_civ": %s,
   "farm_civ": %s, 
   "merchant_civ": %s,
   "treasure-normal": %s,
   "treasure-corner": %s,
   "temple_ruler": %s,
   "settlement_ruler": %s,
   "farm_ruler": %s, 
   "merchant_ruler": %s,
   "points":
       { "temple": %s,
         "settlement": %s,
         "farm": %s,
         "merchant": %s,
         "treasure": %s
       },
    "war_choices": %s,
    "attack":
       { "tiles_available": %s,
         "attack_board": %s,
         "defend_board": %s
       },
    "defend":
       { "tiles_available": %s,
         "defend_board": %s,
         "attack_committed": %s,
         "attack_board": %s
       },
   "defend_internal":
       { "tiles_available": %s,
         "defend_board": %s,
         "attack_committed": %s,
         "attack_board": %s
       },
   "treasure_info":
       {  "must_choose": %s,
          "can_choose": %s,
          "num_choose": %s
       },
   "stats":
       {  "turn_no": %s,
          "action_no": %s,
          "current_turn": %s,
          "waiting_on": %s
       },
   "state": "%s"
}
""" % (ground_moves, war_ground_moves, river_moves, safe_temples, safe_settlements, safe_farms, safe_merchants, safe_reposition_temples, safe_reposition_settlements, safe_reposition_farms, safe_reposition_merchants, war_temples, war_settlements, war_farms, war_merchants, war_reposition_temples, war_reposition_settlements, war_reposition_farms, war_reposition_merchants, hand.count('t'), tiles, board.get_cell_no_for_unification(), board.get_cell_no_for_civ('t') + board.get_cell_no_for_civ('T') + board.get_cell_no_for_civ('T*'), board.get_cell_no_for_civ('s'), board.get_cell_no_for_civ('f'), board.get_cell_no_for_civ('m'), board.get_cell_no_for_civ('T'), board.get_cell_no_for_civ('T*'), board.get_cell_and_player_nos_for_ruler('t'), board.get_cell_and_player_nos_for_ruler('s'), board.get_cell_and_player_nos_for_ruler('f'), board.get_cell_and_player_nos_for_ruler('m'), points['temple'], points['settlement'], points['farm'], points['merchant'], points['treasure'], _find_war_choices(board), attack_info['tiles_available'], attack_info['attack_board'], attack_info['defend_board'], defend_info['tiles_available'], defend_info['defend_board'], defend_info['attack_committed'], defend_info['attack_board'], defend_internal_info['tiles_available'], defend_internal_info['defend_board'], defend_internal_info['attack_committed'], defend_internal_info['attack_board'], treasure_info['must_choose'], treasure_info['can_choose'], treasure_info['num_choose'], g.turn_no, g.action_no, '"' + g.__getattribute__('player_'+str(g.current_turn)).user_name + '"', '"' + g.__getattribute__('player_'+str(g.waiting_for)).user_name + '"', state)
    
#    print str

    resp = HttpResponse(json_str)
    resp.headers['Content-Type'] = 'text/javascript'

    return resp


def _get_internal_war_info(board, player_no, civ_type):
    war_info = []
    for cell_no, cell in enumerate(board):
        if internal_war_ruler(board, cell_no, 'ruler-' + civ_type, player_no):
            kingdom_no = board.data[cell_no]['adjacent_kingdoms'][0]
            for defender_ruler, _, defender_cell in board.pieces_by_region[kingdom_no]['rulers']:
                if defender_ruler == 'ruler-' + civ_type:
                    break
            war_info.append([cell_no, len(board.data[cell_no]['adjacent_temples']), len(board.data[defender_cell]['adjacent_temples'])])

    return war_info

def _find_war_choices(board):
    unification_no = board.find_unification_tile()
    if not unification_no: return []

    kingdom1, kingdom2 = board.data[unification_no]['adjacent_kingdoms']

    kingdom_info1 = board.pieces_by_region[kingdom1]
    kingdom_info2 = board.pieces_by_region[kingdom2]

    civs = []
    for civ in [ 'farm', 'settlement', 'merchant', 'temple' ]:
        if 'ruler-'+civ in [ ruler[0] for ruler in kingdom_info1['rulers'] ] and \
                'ruler-'+civ in [ ruler[0] for ruler in kingdom_info2['rulers'] ]:
            civs.append(civ)

    return civs

# XXX A
def _get_attack_info(game, board):
    attack_info = { 'tiles_available': 0, 'attack_board': 0, 'defend_board': 0 }
    if game.state.split("|")[0] != 'ATTACK': return attack_info

    player = game.waiting_for

    kingdom = _get_attacker_kingdom(game, board)
    if not kingdom: return attack_info
    
    attack_info['attack_board'] = board.pieces_by_region[kingdom][game.state.split("|")[1]]

    hand = Hand.objects.filter(player=game.__getattribute__('player_' + str(player)), turn_no=1, game=game).get()
    attack_info['tiles_available'] =  hand.count(game.state.split("|")[1])

    unification_no = board.find_unification_tile()
    kingdom1, kingdom2 = board.data[unification_no]['adjacent_kingdoms']
    defense_kingdom = kingdom == kingdom1 and kingdom2 or kingdom1
    attack_info['defend_board'] =  board.pieces_by_region[defense_kingdom][game.state.split("|")[1]]
    
    return attack_info

# XXX A
def _get_defend_info(game, board):
    attack_info = { 'tiles_available': 0, 'attack_board': 0, 'defend_board': 0, 'attack_committed': 0 }
    if game.state.split("|")[0] != 'DEFEND': return attack_info

    player = game.waiting_for

    kingdom = _get_defender_kingdom(game, board)
    if not kingdom: return attack_info

    attack_info['defend_board'] = board.pieces_by_region[kingdom][game.state.split("|")[1]]

    hand = Hand.objects.filter(player=game.__getattribute__('player_' + str(player)), turn_no=1, game=game).get()
    attack_info['tiles_available'] =  hand.count(game.state.split("|")[1])

    unification_no = board.find_unification_tile()
    kingdom1, kingdom2 = board.data[unification_no]['adjacent_kingdoms']
    defense_kingdom = kingdom == kingdom1 and kingdom2 or kingdom1
    attack_info['attack_board'] =  board.pieces_by_region[defense_kingdom][game.state.split("|")[1]]

    attack_info['attack_committed'] = game.state.split("|")[2]
    
    return attack_info

# XXX A THIS WHOLE SECTION SUCKS
def _get_kingdom_for_player_in_war(game, board, player):
    unification_no = board.find_unification_tile()
    if not unification_no: return [] 
    # XXX duplicated code
    kingdom1, kingdom2 = board.data[unification_no]['adjacent_kingdoms']

    kingdom_info1 = board.pieces_by_region[kingdom1]
    kingdom_info2 = board.pieces_by_region[kingdom2]
    
    kingdom = None
    for type, player_no, cell_no in kingdom_info1['rulers']:
        if int(player_no) == int(player) and type == ('ruler-' + game.state.split("|")[1]):
            kingdom = kingdom1

    if not kingdom: kingdom = kingdom2
    
    return kingdom

def _get_attacker_kingdom(game, board):
    return _get_kingdom_for_player_in_war(game, board, _get_attacker(game, board))

def _get_defender_kingdom(game, board):
    return _get_kingdom_for_player_in_war(game, board, _get_defender(game, board))

def _get_attacker(game, board):
    return _get_player(game, board, True)

def _get_defender(game, board):
    return _get_player(game, board, False)

# XXX game.current_player is only updated *SOMETIMES*
def _get_player(game, board, find_attacker=True):
    civ = game.state.split("|")[1]

    unification_no = board.find_unification_tile()
    if not unification_no: raise NotInWarException()

    kingdom1, kingdom2 = board.data[unification_no]['adjacent_kingdoms']

    kingdom_info1 = board.pieces_by_region[kingdom1]
    kingdom_info2 = board.pieces_by_region[kingdom2]

    fighters = [ int(player) for type, player, _ in kingdom_info1['rulers'] +kingdom_info2['rulers'] if type == 'ruler-' + civ ]

    player_list = [ (x - 1) % game.num_players + 1 for x in range(int(game.current_turn), int(game.current_turn) + game.num_players) ]
    if not find_attacker: player_list.reverse()
    for num in player_list:
        if num in fighters:
            return num

def _get_internal_defender(game, board, cell_no, civ):
    kingdom = board.data[cell_no]['adjacent_kingdoms'][0]
    ruler_info = board.pieces_by_region[kingdom]['rulers']

    for ruler_type, player_no, _ in ruler_info:
        if ruler_type == 'ruler-' + civ:
            return int(player_no)

    raise NotInWarException

def _get_defend_internal_info(game, board):
    defend_info = { 'tiles_available': 0, 'attack_board': 0, 'defend_board': 0, 'attack_committed': 0 }
    if game.state.split("|")[0] != 'INTERNAL': return defend_info

    _, ruler_type, attack_cell_no, attack_committed = game.state.split("|")
    attack_cell_no = int(attack_cell_no)

    kingdom = board.data[attack_cell_no]['adjacent_kingdoms'][0]
    ruler_info = board.pieces_by_region[kingdom]['rulers']

    for defend_ruler_type, player_no, cell_no in ruler_info:
        if defend_ruler_type == 'ruler-' + ruler_type:
            defend_info['defend_board'] = len(board.data[cell_no]['adjacent_temples'])
            player = player_no
            defend_info['defend_cell_no'] = cell_no

            break

    defend_info['attack_board'] = len(board.data[attack_cell_no]['adjacent_temples'])
    defend_info['attack_committed'] = attack_committed

    hand = Hand.objects.filter(player=game.__getattribute__('player_' + str(player)), turn_no=1, game=game).get()
    defend_info['tiles_available'] =  hand.count('temple')

    defend_info['defend_player'] = player
    defend_info['attack_player'] = game.current_turn
    defend_info['attack_cell_no'] = attack_cell_no
    defend_info['ruler_type'] = ruler_type

    return defend_info


class NotInWarException(Exception):
    pass


def splash(request):
    return render_to_response('splash.html', locals())

def show_games(request):
    games = Game.objects.order_by('id')

    return render_to_response('show_games.html', locals())
