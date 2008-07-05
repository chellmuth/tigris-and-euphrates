from django.conf.urls.defaults import *
from tigris.views import current_datetime, hours_ahead, print_custom_css_board, game_state_json, drop_civ

urlpatterns = patterns('',
    (r'^time/$', current_datetime),
    (r'^time/plus/(\d{1,2})/$', hours_ahead),
    (r'^div/$', print_custom_css_board, { 'rows': 11, 'cols': 16, 'size': 50 }),
    (r'^game_state_json/$', game_state_json),
    (r'^drop_civ/\w*(\d+)/\w*(\d+)/$', drop_civ)

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
