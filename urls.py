from django.conf.urls.defaults import *
from tigris.views import print_custom_css_board, game_state_json, drop_civ, create_game, drop_ruler, external_war, choose_color, attack_commit, defend_commit

urlpatterns = patterns('',
    (r'^div/(\d+)/$', print_custom_css_board, { 'rows': 11, 'cols': 16, 'size': 50 }),
    (r'^game_state_json/(\d+)/$', game_state_json),
    (r'^drop_civ/(\d+)/[^\d]+(\d+)/(\d+)/$', drop_civ),
    (r'^drop_ruler/(\d+)/(\w+)/(\d+)/$', drop_ruler),
    (r'^external_war/(\d+)/[^\d]+(\d+)/(\d+)/$', external_war),
    (r'^create_game/$', create_game),
    (r'^choose_color/(\d)/(\w+)/$', choose_color),
    (r'^attack_commit/(\d)/(\d)/$', attack_commit),
    (r'^defend_commit/(\d)/(\d)/$', defend_commit)
    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
