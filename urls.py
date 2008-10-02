from django.conf.urls.defaults import *
from tigris.views import print_custom_css_board, game_state_json, drop_civ, create_game, drop_ruler, external_war, choose_color, attack_commit, defend_commit, internal_attack, internal_defend, choose_treasure, splash, show_games, reposition_ruler, reposition_ruler_war, remove_ruler

urlpatterns = patterns('',
    (r'^game/(\d+)/(\d+)/$', print_custom_css_board, { 'rows': 11, 'cols': 16, 'size': 50 }),
    (r'^game_state_json/(\d+)/(\d+)/$', game_state_json),
    (r'^drop_civ/(\d+)/(\d+)/[^\d]+(\d+)/(\d+)/$', drop_civ),
    (r'^remove_ruler/(\d+)/(\d)/(\w+)/$', remove_ruler),
    (r'^reposition_ruler/(\d+)/(\d+)/(\w+)/(\d+)/$', reposition_ruler),
    (r'^reposition_ruler_war/(\d+)/(\d)/(\d+)/(\w+)/(\d)/$', reposition_ruler_war),
    (r'^drop_ruler/(\d+)/(\d+)/(\w+)/(\d+)/$', drop_ruler),
    (r'^external_war/(\d+)/(\d+)/[^\d]+(\d+)/(\d+)/$', external_war),
    (r'^create_game/$', create_game),
    (r'^choose_color/(\d+)/(\d)/(\w+)/$', choose_color),
    (r'^attack_commit/(\d+)/(\d)/(\d)/$', attack_commit),
    (r'^defend_commit/(\d+)/(\d)/(\d)/$', defend_commit),
    (r'^internal_attack/(\d+)/(\d)/(\d+)/(\w+)/(\d)/', internal_attack),
    (r'^internal_defend/(\d+)/(\d)/(\d)/', internal_defend),
    (r'^choose_treasure/(\d+)/(\d)/([\d_]+)/', choose_treasure),
    (r'^show_games/', show_games),
    (r'.*', splash),
    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
