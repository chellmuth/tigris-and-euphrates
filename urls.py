from django.conf.urls.defaults import *
from tigris.views import print_custom_css_board, game_state_json, drop_civ

urlpatterns = patterns('',
    (r'^div/$', print_custom_css_board, { 'rows': 11, 'cols': 16, 'size': 50 }),
    (r'^game_state_json/$', game_state_json),
    (r'^drop_civ/[^\d]+(\d+)/[^\d]+(\d+)/$', drop_civ)

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
