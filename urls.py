from django.conf.urls.defaults import *
from tigris.views import current_datetime

urlpatterns = patterns('',
    (r'^time/$', current_datetime),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
